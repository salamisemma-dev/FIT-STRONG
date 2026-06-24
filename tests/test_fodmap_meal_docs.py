import unittest
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DOCS = [
    ROOT / "docs" / "voedingslijst_vrouw_gevoelige_dikke_darm.docx",
    ROOT / "docs" / "fitstrong_combinaties_vrouw_tabellen_grafieken.docx",
]


def docx_text(path: Path) -> str:
    with ZipFile(path) as zf:
        xml = zf.read("word/document.xml")
    root = ET.fromstring(xml)
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    return "\n".join(t.text or "" for t in root.findall(".//w:t", ns))


class TestFodmapMealDocs(unittest.TestCase):
    def test_docs_include_explicit_fodmap_handling(self):
        for path in DOCS:
            with self.subTest(path=path.name):
                text = docx_text(path)
                for expected in [
                    "FODMAP-regels die in dit document zijn gehanteerd",
                    "Groen = dagelijkse basis",
                    "Oranje = testen",
                    "Rood = vermijden",
                    "Witte rijst is uitgesloten",
                    "FODMAP-stacking per maaltijd",
                    "Combinatiecheck",
                ]:
                    self.assertIn(expected, text)

    def test_docs_are_female_fish_vegetable_fruit_oriented(self):
        combined = "\n".join(docx_text(path) for path in DOCS)
        for expected in ["vrouwen", "zalm", "kabeljauw", "courgette", "kiwi", "cyclus"]:
            self.assertIn(expected, combined)


    def test_meal_score_chart_uses_fixed_spacing_image(self):
        from PIL import Image
        import io
        path = ROOT / "docs" / "fitstrong_combinaties_vrouw_tabellen_grafieken.docx"
        with ZipFile(path) as zf:
            image = Image.open(io.BytesIO(zf.read("word/media/image2.png")))
        self.assertEqual((1500, 780), image.size)


if __name__ == "__main__":
    unittest.main()

