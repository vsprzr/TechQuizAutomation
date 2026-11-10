import { AbsoluteFill, Audio, staticFile, useCurrentFrame, interpolate, Sequence } from "remotion";
import quizData from "../public/quiz_data.json";

interface QuizVideoProps {
  revealStartFrame: number;
  outroStartFrame: number;
  audioFrames: number;
}

export const QuizVideo = ({ revealStartFrame = 450, outroStartFrame = 600, audioFrames = 180 }: QuizVideoProps) => {
  const frame = useCurrentFrame();

  const isRevealed = frame >= revealStartFrame;
  const isOutro = frame >= outroStartFrame;
  const isThinkingPhase = frame >= audioFrames && !isRevealed;

  // Countdown timer bar ticks down over the 5-second Think window
  const timerProgress = interpolate(
    frame,
    [audioFrames, revealStartFrame],
    [100, 0],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    }
  );

  // Calculate remaining seconds dynamically for the floating timer (from 5 down to 1)
  const thinkDurationFrames = revealStartFrame - audioFrames;
  const framesIntoThink = frame - audioFrames;
  const remainingSeconds = Math.max(
    1,
    Math.ceil(5 - (framesIntoThink / thinkDurationFrames) * 5)
  );

  // Status text helper
  const statusText = isRevealed ? "CORRECT ANSWER" : isThinkingPhase ? `THINKING... (${remainingSeconds}s)` : "LISTENING TO QUESTION...";
  const statusBgColor = isRevealed ? "#064e3b" : isThinkingPhase ? "#78350f" : "#1e3a8a";
  const statusBorderColor = isRevealed ? "#22c55e" : isThinkingPhase ? "#f59e0b" : "#3b82f6";
  const statusTextColor = isRevealed ? "#d1fae5" : isThinkingPhase ? "#fef3c7" : "#dbeafe";

  return (
    <AbsoluteFill style={{ backgroundColor: "#0f172a", display: "flex", flexDirection: "column", justifyContent: "flex-start", alignItems: "center", fontFamily: "Helvetica, Arial, sans-serif", padding: "85px 60px 50px 60px" }}>
      {/* 1. Play Initial Question Voiceover */}
      <Audio src={staticFile("voiceover.mp3")} />

      {/* 2. Play Answer & Explanation Voiceover precisely when the answer is revealed */}
      {isRevealed && !isOutro && (
        <Sequence from={revealStartFrame}>
          <Audio src={staticFile("answer_audio.mp3")} />
        </Sequence>
      )}

      {/* OUTRO SCREEN */}
      {isOutro ? (
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", textAlign: "center", gap: "20px", width: "100%", height: "100%" }}>
          <div style={{ fontSize: "78px" }}>🚀</div>
          <h1 style={{ color: "#f8fafc", fontSize: "64px", margin: 0 }}>Like & Follow</h1>
          <p style={{ color: "#38bdf8", fontSize: "44px", margin: 0 }}>For daily tech trivia!</p>
        </div>
      ) : (
        /* MAIN QUIZ SCREEN */
        <>
          {/* Top Header: Title & Progress Bar */}
          <div style={{ width: "100%", display: "flex", flexDirection: "column", gap: "12px", flexShrink: 0 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span style={{ color: "#38bdf8", fontSize: "44px", fontWeight: "bold", textTransform: "uppercase", letterSpacing: "1px" }}>
                ⚡ Tech Trivia Quiz
              </span>
            </div>

            {/* Countdown Bar */}
            <div style={{ width: "100%", height: "12px", backgroundColor: "#1e293b", borderRadius: "6px", overflow: "hidden" }}>
              <div style={{ width: `${isRevealed ? 0 : isThinkingPhase ? timerProgress : 100}%`, height: "100%", backgroundColor: isRevealed ? "#22c55e" : "#38bdf8", transition: "width 0.1s linear" }} />
            </div>
          </div>

          {/* Spacer Before Status Banner */}
          <div style={{ height: "52px", minHeight: "52px", width: "100%", flexShrink: 0 }} />

          {/* Prominent Status Banner */}
          <div style={{ backgroundColor: statusBgColor, border: `2px solid ${statusBorderColor}`, padding: "16px 24px", borderRadius: "16px", textAlign: "center", boxShadow: "0 10px 15px -3px rgb(0 0 0 / 0.4)", width: "100%", flexShrink: 0 }}>
            <span style={{ color: statusTextColor, fontSize: "36px", fontWeight: "bold", letterSpacing: "1px", textTransform: "uppercase" }}>
              {statusText}
            </span>
          </div>

          {/* Spacer After Status Banner / Before Question Box */}
          <div style={{ height: "52px", minHeight: "52px", width: "100%", flexShrink: 0 }} />

          {/* Question Box */}
          <div style={{ backgroundColor: "#1e293b", padding: "36px", borderRadius: "24px", border: "2px solid #334155", boxShadow: "0 20px 25px -5px rgb(0 0 0 / 0.5)", width: "100%", flexShrink: 0 }}>
            <h2 style={{ color: "#f8fafc", fontSize: "46px", lineHeight: "1.4", margin: 0 }}>
              {quizData.question}
            </h2>
          </div>

          {/* Options List */}
          <div style={{ display: "flex", flexDirection: "column", width: "100%", gap: "18px", marginTop: "25px", flexShrink: 0 }}>
            {quizData.options.map((option, index) => {
              const isCorrect = option === quizData.correct_answer;
              
              let bgColor = "#1e293b";
              let borderColor = "#334155";
              let textColor = "#e2e8f0";

              if (isRevealed && isCorrect) {
                bgColor = "#064e3b"; // Dark green
                borderColor = "#22c55e"; // Bright green
                textColor = "#d1fae5";
              } else if (isRevealed && !isCorrect) {
                bgColor = "#1e293b";
                borderColor = "#334155";
                textColor = "#64748b"; // Dim incorrect options
              }

              return (
                <div key={index} style={{ backgroundColor: bgColor, padding: "24px", borderRadius: "16px", color: textColor, fontSize: "38px", border: `2px solid ${borderColor}`, display: "flex", alignItems: "center", gap: "20px", transition: "all 0.3s ease" }}>
                  <span style={{ backgroundColor: isRevealed && isCorrect ? "#22c55e" : "#334155", color: isRevealed && isCorrect ? "#000" : "#cbd5e1", width: "52px", height: "52px", borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: "bold", flexShrink: 0, fontSize: "28px" }}>
                    {String.fromCharCode(65 + index)}
                  </span>
                  <span>{option}</span>
                </div>
              );
            })}
          </div>

          {/* Explanation Box */}
          {isRevealed && (
            <div style={{ marginTop: "20px", width: "100%", backgroundColor: "#022c22", border: "2px solid #059669", padding: "22px", borderRadius: "16px", flexShrink: 0 }}>
              <p style={{ color: "#a7f3d0", fontSize: "34px", margin: 0, lineHeight: "1.4" }}>
                💡 <strong>Explanation:</strong> {quizData.explanation}
              </p>
            </div>
          )}
        </>
      )}
    </AbsoluteFill>
  );
};
