import { Composition } from "remotion";
import { QuizVideo } from "./QuizVideo";
import { getAudioDurationInSeconds } from "@remotion/media-utils";
import { staticFile } from "remotion";

export const Root = () => {
  return (
    <Composition
      id="Root"
      component={QuizVideo}
      durationInFrames={300} // Fallback default
      fps={30}
      width={1080}
      height={1920}
      calculateMetadata={async () => {
        const fps = 30;
        let questionAudioSec = 5;
        let answerAudioSec = 5;
        
        try {
          questionAudioSec = await getAudioDurationInSeconds(staticFile("voiceover.mp3"));
        } catch (e) {
          console.log("Using default question audio duration.");
        }

        try {
          answerAudioSec = await getAudioDurationInSeconds(staticFile("answer_audio.mp3"));
        } catch (e) {
          console.log("Using default answer audio duration.");
        }

        const audioFrames = Math.ceil(questionAudioSec * fps);
        const thinkFrames = 5 * fps; // 5-second think window (150 frames)
        const revealStart = audioFrames + thinkFrames;
        
        // Give the answer page enough time to fully play the answer audio + padding
        const answerAudioFrames = Math.ceil(answerAudioSec * fps);
        const explanationFrames = Math.max(7 * fps, answerAudioFrames + 30); 
        const outroStart = revealStart + explanationFrames;
        
        const outroFrames = 3 * fps; // 3-second outro (90 frames)
        const totalFrames = outroStart + outroFrames;

        return {
          durationInFrames: totalFrames,
          props: {
            revealStartFrame: revealStart,
            outroStartFrame: outroStart,
            audioFrames: audioFrames,
          },
        };
      }}
    />
  );
};
