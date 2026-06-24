// Generates templates/voedingsdagboek_template.docx — a fillable NL daily food diary
// whose fields map to the fit_strong engine intake. Run: node scripts/make_diary_template.mjs
import {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  AlignmentType, HeadingLevel, BorderStyle, WidthType, ShadingType, VerticalAlign,
} from "docx";
import { writeFileSync, mkdirSync } from "node:fs";

const CONTENT = 9026; // A4, 1" margins (DXA)
const HEADER_FILL = "16A085";
const LABEL_FILL = "E8F6F3";
const border = { style: BorderStyle.SINGLE, size: 1, color: "BDC3C7" };
const borders = { top: border, bottom: border, left: border, right: border };
const cellMargins = { top: 90, bottom: 90, left: 120, right: 120 };

function cell(text, width, { head = false, label = false, bold = false, blankLines = 0, align } = {}) {
  const children = [new Paragraph({
    alignment: align,
    children: [new TextRun({ text, bold: bold || head, color: head ? "FFFFFF" : "2C3E50",
      size: head ? 20 : 22 })],
  })];
  for (let i = 0; i < blankLines; i++) children.push(new Paragraph({ children: [new TextRun("")] }));
  return new TableCell({
    borders, width: { size: width, type: WidthType.DXA }, margins: cellMargins,
    verticalAlign: VerticalAlign.CENTER,
    shading: head ? { fill: HEADER_FILL, type: ShadingType.CLEAR }
      : label ? { fill: LABEL_FILL, type: ShadingType.CLEAR } : undefined,
    children,
  });
}

function headerRow(cols, widths) {
  return new TableRow({
    tableHeader: true,
    children: cols.map((c, i) => cell(c, widths[i], { head: true })),
  });
}

function table(widths, rows) {
  return new Table({ width: { size: CONTENT, type: WidthType.DXA }, columnWidths: widths, rows });
}

function h2(text) {
  return new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(text)] });
}
function spacer() { return new Paragraph({ children: [new TextRun("")] }); }
function note(text) {
  return new Paragraph({ children: [new TextRun({ text, italics: true, size: 18, color: "7F8C8D" })] });
}

// ---- Intake (eenmalig) ----
const intakeRows = [
  ["Gewicht (kg)", ""],
  ["Lengte (cm)", ""],
  ["Geslacht (m / v / anders)", ""],
  ["Doel (spiermassa / uithouding / algeheel)", ""],
  ["Sporturen per week", ""],
].map(([k]) => new TableRow({ children: [
  cell(k, 4513, { label: true, bold: true }),
  cell("", 4513),
]}));

// ---- Maaltijden ----
const mealHead = headerRow(
  ["Tijd", "Voedingsmiddelen + hoeveelheid (gram)", "FODMAP (optioneel)", "Notities"],
  [1000, 4826, 1700, 1500],
);
const mealRows = Array.from({ length: 6 }, () => new TableRow({ children: [
  cell("", 1000, { blankLines: 1 }),
  cell("", 4826, { blankLines: 1 }),
  cell("", 1700, { blankLines: 1 }),
  cell("", 1500, { blankLines: 1 }),
]}));

// ---- Klachten (vandaag) ----
const klachtHead = headerRow(
  ["Tijd", "Bristol (1-7)", "Buikpijn (0-10)", "Opgeblazen (0-10)", "Energie (1-10)"],
  [1626, 1850, 1850, 1850, 1850],
);
const klachtRows = Array.from({ length: 2 }, () => new TableRow({ children: [
  cell("", 1626, { blankLines: 1 }),
  cell("", 1850, { blankLines: 1, align: AlignmentType.CENTER }),
  cell("", 1850, { blankLines: 1, align: AlignmentType.CENTER }),
  cell("", 1850, { blankLines: 1, align: AlignmentType.CENTER }),
  cell("", 1850, { blankLines: 1, align: AlignmentType.CENTER }),
]}));

// ---- Training ----
const trainHead = headerRow(["Tijd", "Duur (min)", "Intensiteit (1-10)", "Type"], [2256, 2256, 2257, 2257]);
const trainRows = Array.from({ length: 2 }, () => new TableRow({ children: [
  cell("", 2256, { blankLines: 1 }),
  cell("", 2256, { blankLines: 1, align: AlignmentType.CENTER }),
  cell("", 2257, { blankLines: 1, align: AlignmentType.CENTER }),
  cell("", 2257, { blankLines: 1 }),
]}));

// ---- Dagtotalen ----
const totalRows = [
  ["Calorieën (kcal) — schatting", ""],
  ["Eiwit (g) — schatting", ""],
].map(([k]) => new TableRow({ children: [
  cell(k, 4513, { label: true, bold: true }),
  cell("", 4513),
]}));

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 34, bold: true, font: "Arial", color: "16A085" },
        paragraph: { spacing: { after: 120 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: "Arial", color: "2C3E50" },
        paragraph: { spacing: { before: 260, after: 120 }, outlineLevel: 1 } },
    ],
  },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 },
      margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    children: [
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Fit & Strong — Voedingsdagboek")] }),
      new Paragraph({ children: [
        new TextRun({ text: "Datum: ____________________", size: 22 }),
        new TextRun({ text: "\tDag: ____________________", size: 22 }),
      ], tabStops: [{ type: "right", position: 9026 }] }),
      note("Vul per dag in. Wees concreet met hoeveelheden (gram of huishoudmaat). Eén bestand per dag."),

      h2("Intake (1× invullen — verandert zelden)"),
      table([4513, 4513], intakeRows),

      h2("Maaltijden"),
      table([1000, 4826, 1700, 1500], [mealHead, ...mealRows]),
      note("FODMAP-niveau (optioneel): hoog / middel / laag / zeer laag. Bijv. ui & knoflook = hoog; rijst & kip = zeer laag."),

      h2("Klachten (vandaag)"),
      table([1626, 1850, 1850, 1850, 1850], [klachtHead, ...klachtRows]),
      note("Bristol: 1 = harde keutels, 4 = ideaal, 7 = waterig. Buikpijn/opgeblazen: 0 = geen, 10 = ergst. Energie: 1 = slap, 10 = topfit."),

      h2("Training"),
      table([2256, 2256, 2257, 2257], [trainHead, ...trainRows]),

      h2("Dagtotalen (schatting)"),
      table([4513, 4513], totalRows),
      note("Calorieën/eiwit mogen schattingen zijn. Onbekend? Laat leeg — de engine verzint niets en slaat dat deel over."),

      spacer(),
      new Paragraph({
        border: { top: { style: BorderStyle.SINGLE, size: 6, color: "16A085", space: 6 } },
        children: [new TextRun({
          text: "Indicatief hulpmiddel, geen medisch advies. Bij aanhoudende klachten: raadpleeg een (sport)diëtist of arts.",
          italics: true, size: 18, color: "7F8C8D" })],
      }),
    ],
  }],
});

mkdirSync("templates", { recursive: true });
const out = "templates/voedingsdagboek_template.docx";
Packer.toBuffer(doc).then((buf) => { writeFileSync(out, buf); console.log("written", out, buf.length, "bytes"); });
