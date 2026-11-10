import { AbsoluteFill, Audio, staticFile, useCurrentFrame } from "remotion";
import quizData from "./public/quiz_data.json";

export const QuizVideo = () => {
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill style={{ backgroundColor: "#0f172a", justifyContent: "center", alignItems: "center", fontFamily: "Helvetica, Arial, sans-serif", padding: "60px" }}>
      {/* Background Music Track set to low volume (12%) to sit cleanly under voiceover */}
      <Audio src={staticFile("background_music.mp3")} volume={0.12} />

      {/* Play Google Cloud Studio Voiceover Audio */}
      <Audio src={staticFile("voiceover.mp3")} />

      {/* Header */}
      <div style={{ position: "absolute", top: "120px", color: "#38bdf8", fontSize: "40px", fontWeight: "bold", textTransform: "uppercase", letterSpacing: "2px" }}>
        ⚡ TECH TRIVIA QUIZ
      </div>

      {/* Question Box */}
      <div style={{ backgroundColor: "#1e293b", padding: "40px", borderRadius: "24px", width: "90%", border: "2px solid #334155", boxShadow: "0 20px 25px -5px rgb(0 0 0 / 0.5)", marginBottom: "50px" }}>
        <h2 style={{ color: "#f8fafc", fontSize: "44px", lineHeight: "1.4", margin: 0 }}>
          {quizData.question}
        </h2>
      </div>

      {/* Options List */}
      <div style={{ display: "flex", flexDirection: "column", width: "90%", gap: "20px" }}>
        {quizData.options.map((option, index) => {
          return (
            <div key={index} style={{ backgroundColor: "#1e293b", padding: "30px", borderRadius: "16px", color: "#e2e8f0", fontSize: "36px", border: "2px solid #334155", display: "flex", alignItems: "center", gap: "20px" }}>
              <span style={{ backgroundColor: "#334155", color: "#cbd5e1", width: "50px", height: "50px", borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: "bold", flexShrink: 0 }}>
                {String.fromCharCode(65 + index)}
              </span>
              <span>{option}</span>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};