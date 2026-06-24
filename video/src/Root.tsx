import { Composition } from "remotion";
import { WeeklyRecap, weeklyRecapSchema, defaultProps } from "./WeeklyRecap";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="WeeklyRecap"
      component={WeeklyRecap}
      durationInFrames={240}
      fps={30}
      width={1080}
      height={1080}
      schema={weeklyRecapSchema}
      defaultProps={defaultProps}
    />
  );
};
