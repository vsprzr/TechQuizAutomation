import { Composition } from "remotion";
import { QuizVideo } from "./QuizVideo";

export const Root = () => {
  return (
    <Composition
      id="Root"
      component={QuizVideo}
      durationInFrames={150} // 5 seconds at 30fps as default; audio length will drive it
      fps={30}
      width={1080}
      height={1920} // Vertical 9:16 format for Shorts/Reels
    />
  );
};
