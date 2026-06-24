import unittest
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def docx_text(path: Path) -> str:
    with ZipFile(path) as zf:
        xml = zf.read("word/document.xml")
    root = ET.fromstring(xml)
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    return "\n".join(t.text or "" for t in root.findall(".//w:t", ns))


class TestIntakeTemplates(unittest.TestCase):
    def test_male_template_has_shared_daily_fields_without_cycle_requirement(self):
        text = docx_text(ROOT / "templates" / "voedingsdagboek_template_man.docx")
        for expected in [
            "Voedingsdagboek man",
            "Maaltijden & drinken",
            "Supplementen & medicatie",
            "Klachten, ontlasting & energie",
            "Training & herstel",
            "Dagtotalen",
            "Klaar voor analyse",
            "Laat onbekend leeg",
        ]:
            self.assertIn(expected, text)
        self.assertNotIn("Cycluscontext", text)

    def test_female_template_has_optional_cycle_context(self):
        text = docx_text(ROOT / "templates" / "voedingsdagboek_template_vrouw.docx")
        for expected in [
            "Voedingsdagboek vrouw",
            "Maaltijden & drinken",
            "Supplementen & medicatie",
            "Cycluscontext",
            "Cycle wellbeing",
            "niet als diagnose",
        ]:
            self.assertIn(expected, text)

    def test_app_pva_is_novice_first_and_exports_to_engine(self):
        text = (ROOT / "docs" / "APP_PVA.md").read_text(encoding="utf-8")
        for expected in [
            "Leek-modus eerst",
            "Export",
            "engine-klare JSON",
            "Voor- en nadelen met fix",
            "localStorage/IndexedDB",
        ]:
            self.assertIn(expected, text)


if __name__ == "__main__":
    unittest.main()


