import { AbsoluteFill, interpolate, useCurrentFrame, spring, useVideoConfig } from "remotion";
import { z } from "zod";

// Mirror of fit_strong.weekly_video_props output (spec-report-artifacts).
export const weeklyRecapSchema = z.object({
  week_label: z.string(),
  score: z.number(),
  band: z.string(),
  subscores: z.record(z.number()),
  top_improvements: z.array(
    z.object({ area: z.string(), score: z.number(), action: z.string() })
  ),
  disclaimer: z.string(),
});

export type WeeklyRecapProps = z.infer<typeof weeklyRecapSchema>;

export const defaultProps: WeeklyRecapProps = {
  week_label: "Voorbeeldweek",
  score: 67,
  band: "goed",
  subscores: { protein: 80, energy: 70, microbiome: 60, fodmap: 65 },
  top_improvements: [
    { area: "microbiome", score: 60, action: "Bouw vezels/prebiotica op." },
  ],
  disclaimer: "Indicatief, geen medisch advies.",
};

const BAND_COLOR: Record<string, string> = {
  "aandacht nodig": "#c0392b",
  matig: "#e67e22",
  goed: "#27ae60",
  sterk: "#16a085",
};

export const WeeklyRecap: React.FC<WeeklyRecapProps> = (props) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const color = BAND_COLOR[props.band] ?? "#27ae60";

  const appear = spring({ frame, fps, config: { damping: 200 } });
  const shown = Math.round(interpolate(appear, [0, 1], [0, props.score]));
  const fadeIn = interpolate(frame, [50, 80], [0, 1], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ backgroundColor: "#0f1419", color: "#ecf0f1", fontFamily: "sans-serif", padding: 80 }}>
      <div style={{ fontSize: 36, opacity: 0.7 }}>{props.week_label}</div>
      <div style={{ fontSize: 40, marginTop: 8 }}>Fit &amp; Strong</div>
      <div style={{ fontSize: 280, fontWeight: 800, color, lineHeight: 1.1 }}>{shown}</div>
      <div style={{ fontSize: 48, color }}>{props.band}</div>
      <div style={{ marginTop: 40, opacity: fadeIn }}>
        <div style={{ fontSize: 32, marginBottom: 12 }}>Wat kan beter:</div>
        {props.top_improvements.map((imp) => (
          <div key={imp.area} style={{ fontSize: 28, opacity: 0.85, marginBottom: 8 }}>
            • {imp.area} ({imp.score}/100)
          </div>
        ))}
      </div>
      <div style={{ position: "absolute", bottom: 40, left: 80, right: 80, fontSize: 20, opacity: 0.5 }}>
        {props.disclaimer}
      </div>
    </AbsoluteFill>
  );
};
