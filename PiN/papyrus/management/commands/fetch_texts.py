from urllib.parse import urlparse
from urllib.request import urlopen
from xml.etree import ElementTree as ET

from django.core.management.base import BaseCommand

from papyrus.models import PapyrusSide


class Command(BaseCommand):
    help = (
        "Fetch XML from papyri.info links and populate PapyrusSide.text with the "
        "contents of <text><body>."
    )

    ICON_START = "🚀"
    ICON_INFO = "ℹ️"
    ICON_LINK = "🔗"
    ICON_FETCH = "🌐"
    ICON_PARSE = "🧾"
    ICON_SAVE = "💾"
    ICON_SKIP = "⏭️"
    ICON_FAIL = "❌"
    ICON_DONE = "✅"

    COLOR_RESET = "\033[0m"
    COLOR_CYAN = "\033[96m"
    COLOR_BLUE = "\033[94m"
    COLOR_MAGENTA = "\033[95m"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._use_color = True

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Overwrite existing PapyrusSide.text values.",
        )
        parser.add_argument(
            "--timeout",
            type=int,
            default=20,
            help="HTTP timeout in seconds (default: 20).",
        )

    def handle(self, *args, **options):
        force = options["force"]
        timeout = options["timeout"]
        self._use_color = options.get("force_color") or not options.get("no_color")

        total = 0
        updated = 0
        skipped = 0
        failed = 0

        self._log_heading(f"{self.ICON_START} Starting fetch_texts")
        self._log_info(f"Force overwrite: {'yes' if force else 'no'}")
        self._log_info(f"Timeout: {timeout}s")

        queryset = PapyrusSide.objects.select_related("papyrus").prefetch_related("papyrus__links")
        self._log_info(f"Loaded {queryset.count()} papyrus sides")

        for side in queryset:
            total += 1
            self._log_heading(f"\n{self.ICON_INFO} Side {side.pk} | {side.publication}")

            if side.text and not force:
                skipped += 1
                self._log_warning(
                    f"{self.ICON_SKIP} Skipped: text already present (use --force to overwrite)."
                )
                continue

            papyri_links = [
                link.url for link in side.papyrus.links.all() if "papyri.info" in (link.url or "")
            ]

            self._log_info(f"Found {len(papyri_links)} papyri.info link(s) on papyrus {side.papyrus_id}.")

            if not papyri_links:
                skipped += 1
                self._log_warning(f"{self.ICON_SKIP} Skipped: no papyri.info links.")
                continue

            extracted_text = None
            last_error = None

            for link in papyri_links:
                self._log_step(f"{self.ICON_LINK} Candidate URL: {link}", self.COLOR_BLUE)
                xml_url = self._to_source_url(link)
                self._log_step(f"{self.ICON_FETCH} Fetching source XML: {xml_url}", self.COLOR_CYAN)
                try:
                    xml_bytes = self._fetch_xml(xml_url, timeout=timeout)
                    self._log_step(
                        f"{self.ICON_PARSE} XML fetched ({len(xml_bytes)} bytes). Extracting <text><body>...",
                        self.COLOR_MAGENTA,
                    )
                    extracted_text = self._extract_body_text(xml_bytes)
                    if extracted_text:
                        self._log_success(
                            f"{self.ICON_PARSE} Extracted {len(extracted_text)} characters from <text><body>."
                        )
                        break
                    last_error = "No <text><body> content found"
                    self._log_warning(f"{self.ICON_SKIP} {last_error}")
                except Exception as exc:  # noqa: BLE001
                    last_error = str(exc)
                    self._log_error(f"{self.ICON_FAIL} Fetch/parse error: {last_error}")

            if not extracted_text:
                failed += 1
                self._log_error(
                    f"{self.ICON_FAIL} Failed side {side.pk}: {last_error or 'Unable to extract text'}"
                )
                continue

            side.text = extracted_text
            side.save(update_fields=["text"])
            updated += 1
            self._log_success(f"{self.ICON_SAVE} Saved text to side {side.pk}.")

        self._log_heading("\n" + "=" * 60)
        self._log_success(
            f"{self.ICON_DONE} Done. Processed={total}, Updated={updated}, Skipped={skipped}, Failed={failed}"
        )

    def _to_source_url(self, url):
        parsed = urlparse(url)
        path = parsed.path or ""

        if path.endswith("/source"):
            return url

        if path.endswith("/"):
            path = path[:-1]

        new_path = f"{path}/source"
        return parsed._replace(path=new_path, query="", fragment="").geturl()

    def _fetch_xml(self, url, timeout):
        with urlopen(url, timeout=timeout) as response:
            return response.read()

    def _extract_body_text(self, xml_bytes):
        root = ET.fromstring(xml_bytes)

        body = root.find(".//{*}text/{*}body")
        if body is None:
            body = root.find(".//body")

        if body is None:
            return None

        edition_divs = body.findall(".//{*}div[@type='edition']")
        if not edition_divs:
            edition_divs = body.findall(".//div[@type='edition']")

        if not edition_divs:
            return None

        text_chunks = []
        for div in edition_divs:
            div_text = "".join(div.itertext()).strip()
            if div_text:
                text_chunks.append(div_text)

        text_content = "\n\n".join(text_chunks).strip()
        return text_content or None

    def _paint(self, text, color_code):
        if not self._use_color:
            return text
        return f"{color_code}{text}{self.COLOR_RESET}"

    def _log_heading(self, message):
        self.stdout.write(self._paint(message, self.COLOR_CYAN))

    def _log_info(self, message):
        self.stdout.write(self._paint(message, self.COLOR_BLUE))

    def _log_step(self, message, color_code):
        self.stdout.write(self._paint(message, color_code))

    def _log_warning(self, message):
        self.stdout.write(self.style.WARNING(message))

    def _log_error(self, message):
        self.stdout.write(self.style.ERROR(message))

    def _log_success(self, message):
        self.stdout.write(self.style.SUCCESS(message))
