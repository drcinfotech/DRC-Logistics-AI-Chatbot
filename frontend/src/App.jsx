import { useEffect, useRef, useState } from "react";
import {
  Send, RefreshCw, Phone, MoreHorizontal, CheckCircle2, Truck,
  ShieldAlert, Navigation,
} from "lucide-react";
import { sendMessage, getHealth } from "./api";
import Block from "./components/Blocks";

const ACCENT = "#6BA5FF";

const INITIAL_GREETING = {
  blocks: [
    {
      type: "text",
      content:
        "Hi, I'm Routara — your logistics companion. I can track shipments, quote shipping rates, schedule pickups, check fleet and warehouse status, file claims, and more. What would you like to do?",
    },
  ],
  suggestions: ["Track a shipment", "Get a shipping quote", "My shipments", "Service options"],
};

function TypingDots() {
  return (
    <div className="flex gap-1 items-center px-3 py-2.5 rounded-2xl rounded-tl-md" style={{ background: "rgba(255,255,255,0.03)" }}>
      {[0, 1, 2].map((i) => (
        <span
          key={i}
          className="block rounded-full"
          style={{
            width: 5, height: 5, background: ACCENT,
            animation: "bounceDot 1.4s infinite",
            animationDelay: `${i * 0.15}s`,
          }}
        />
      ))}
      <style>{`@keyframes bounceDot { 0%,80%,100% { opacity:0.3; transform:scale(0.7) } 40% { opacity:1; transform:scale(1) } }`}</style>
    </div>
  );
}

export default function App() {
  const [messages, setMessages] = useState([{ role: "bot", ...INITIAL_GREETING }]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [backendUp, setBackendUp] = useState(null);
  const scrollRef = useRef(null);

  useEffect(() => {
    getHealth().then(() => setBackendUp(true)).catch(() => setBackendUp(false));
  }, []);

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [messages, loading]);

  const currentSuggestions = (() => {
    for (let i = messages.length - 1; i >= 0; i--) {
      if (messages[i].role === "bot" && messages[i].suggestions) return messages[i].suggestions;
    }
    return [];
  })();

  async function send(text) {
    const trimmed = (text ?? input).trim();
    if (!trimmed || loading) return;
    setMessages((m) => [...m, { role: "user", content: trimmed }]);
    setInput("");
    setLoading(true);
    try {
      const data = await sendMessage(trimmed, sessionId);
      if (!sessionId) setSessionId(data.session_id);
      setMessages((m) => [...m, { role: "bot", blocks: data.blocks, suggestions: data.suggestions, safetyFlag: data.safety_flag }]);
    } catch (e) {
      setMessages((m) => [...m, {
        role: "bot",
        blocks: [{ type: "text", content: "I'm having trouble reaching the server. Make sure the backend is running on port 8000." }],
        suggestions: ["Retry"],
      }]);
    } finally {
      setLoading(false);
    }
  }

  function resetSession() {
    setMessages([{ role: "bot", ...INITIAL_GREETING }]);
    setSessionId(null);
  }

  return (
    <div style={{
      background: "radial-gradient(ellipse at top right, #0C1A2E 0%, #080F1C 50%, #050506 100%)",
      color: "rgba(255,255,255,0.9)",
      minHeight: "100vh",
    }}>
      <div className="fixed inset-0 pointer-events-none grain" />

      <div className="relative mx-auto px-6 py-8" style={{ maxWidth: 1400 }}>
        {/* Header */}
        <header className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center border"
              style={{ background: "linear-gradient(135deg, rgba(255,255,255,0.06), rgba(255,255,255,0.01))", borderColor: "rgba(255,255,255,0.08)" }}>
              <Truck size={15} style={{ color: ACCENT }} />
            </div>
            <div>
              <div className="text-xs uppercase tracking-tightest3" style={{ color: "rgba(255,255,255,0.4)" }}>
                Logistics AI Chatbot
              </div>
              <div className="text-lg font-serif" style={{ color: "white" }}>
                Routara<span style={{ color: ACCENT }}>.</span>
                <span style={{ color: "rgba(255,255,255,0.4)" }}> Your logistics companion.</span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="hidden md:flex items-center gap-2 text-11">
              <div style={{ width: 8, height: 8, borderRadius: "50%", background: backendUp === false ? "#fca5a5" : "#86efac" }} />
              <span style={{ color: "rgba(255,255,255,0.45)" }}>{backendUp === false ? "Backend offline" : "Backend online"}</span>
            </div>
            <button onClick={resetSession}
              className="flex items-center gap-1.5 text-11 px-3 py-1.5 rounded-full border transition hover:bg-white/5"
              style={{ borderColor: "rgba(255,255,255,0.08)", color: "rgba(255,255,255,0.6)" }}>
              <RefreshCw size={11} /> New session
            </button>
          </div>
        </header>

        {/* Grid */}
        <div className="grid gap-6" style={{ gridTemplateColumns: "1fr 340px" }}>
          {/* Chat panel */}
          <div className="rounded-3xl border overflow-hidden flex flex-col"
            style={{
              background: "linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.005))",
              borderColor: "rgba(255,255,255,0.08)",
              height: 720,
            }}>
            <div className="px-5 py-4 border-b flex items-center justify-between"
              style={{ borderColor: "rgba(255,255,255,0.06)" }}>
              <div className="flex items-center gap-3">
                <div className="relative">
                  <div className="w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium border-2 font-serif"
                    style={{ background: `linear-gradient(135deg, ${ACCENT}33, ${ACCENT}0A)`, borderColor: `${ACCENT}44`, color: ACCENT }}>
                    R
                  </div>
                  <div className="absolute animate-pulse-ring"
                    style={{ bottom: -2, right: -2, width: 12, height: 12, borderRadius: "50%", border: "2px solid #0A0A0A", background: ACCENT }} />
                </div>
                <div>
                  <div className="text-sm font-medium" style={{ color: "white" }}>Routara</div>
                  <div className="text-11" style={{ color: "rgba(255,255,255,0.4)" }}>AI logistics companion</div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button className="w-8 h-8 rounded-full flex items-center justify-center hover:bg-white/5" style={{ color: "rgba(255,255,255,0.5)" }}><Phone size={13} /></button>
                <button className="w-8 h-8 rounded-full flex items-center justify-center hover:bg-white/5" style={{ color: "rgba(255,255,255,0.5)" }}><MoreHorizontal size={13} /></button>
              </div>
            </div>

            <div ref={scrollRef} className="flex-1 overflow-y-auto px-5 py-5 space-y-3 scrollbar">
              {messages.map((m, mi) =>
                m.role === "user" ? (
                  <div key={mi} className="flex justify-end animate-fade-up">
                    <div className="text-sm px-4 py-2.5 rounded-2xl"
                      style={{ background: "rgba(255,255,255,0.06)", color: "rgba(255,255,255,0.95)", borderBottomRightRadius: 6, maxWidth: "80%" }}>
                      {m.content}
                    </div>
                  </div>
                ) : (
                  <div key={mi} className="flex gap-2.5 animate-fade-up">
                    <div className="rounded-full flex items-center justify-center text-11 font-medium border font-serif flex-shrink-0"
                      style={{ width: 28, height: 28, marginTop: 2, background: ACCENT + "14", borderColor: ACCENT + "33", color: ACCENT }}>
                      R
                    </div>
                    <div className="space-y-2 flex-1 min-w-0" style={{ maxWidth: "85%" }}>
                      {m.blocks.map((b, bi) => <Block key={bi} block={b} />)}
                    </div>
                  </div>
                )
              )}
              {loading && (
                <div className="flex gap-2.5 animate-fade-up">
                  <div className="rounded-full flex items-center justify-center text-11 font-medium border font-serif flex-shrink-0"
                    style={{ width: 28, height: 28, marginTop: 2, background: ACCENT + "14", borderColor: ACCENT + "33", color: ACCENT }}>
                    R
                  </div>
                  <TypingDots />
                </div>
              )}
            </div>

            <div className="px-5 pt-3 pb-3 border-t" style={{ borderColor: "rgba(255,255,255,0.06)" }}>
              {currentSuggestions.length > 0 && (
                <div className="flex gap-1.5 overflow-x-auto mb-3 px-1 scrollbar" style={{ marginLeft: -4, marginRight: -4 }}>
                  {currentSuggestions.map((s, i) => (
                    <button key={i} onClick={() => send(s)} disabled={loading}
                      className="text-11 px-3 py-1.5 rounded-full border whitespace-nowrap transition hover:bg-white/5 disabled:opacity-40"
                      style={{ background: "rgba(255,255,255,0.02)", borderColor: "rgba(255,255,255,0.08)", color: "rgba(255,255,255,0.7)" }}>
                      {s}
                    </button>
                  ))}
                </div>
              )}
              <div className="flex items-center gap-2">
                <input type="text" value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && send()}
                  placeholder="Message Routara…" disabled={loading}
                  className="flex-1 text-sm px-4 py-2.5 rounded-xl border bg-transparent disabled:opacity-50"
                  style={{ color: "white", borderColor: "rgba(255,255,255,0.08)" }} />
                <button onClick={() => send()} disabled={loading || !input.trim()}
                  className="rounded-xl flex items-center justify-center disabled:opacity-40"
                  style={{ width: 40, height: 40, background: ACCENT, color: "#0A0A0A" }}>
                  <Send size={14} />
                </button>
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <aside className="space-y-4">
            <div className="rounded-2xl border p-5 overflow-hidden relative"
              style={{ background: `linear-gradient(180deg, ${ACCENT}14, rgba(255,255,255,0.005))`, borderColor: `${ACCENT}22` }}>
              <div className="absolute"
                style={{ top: -48, right: -48, width: 128, height: 128, borderRadius: "50%", filter: "blur(60px)", opacity: 0.4, background: ACCENT }} />
              <div className="relative">
                <div className="flex items-center gap-2 mb-3">
                  <Truck size={14} style={{ color: ACCENT }} />
                  <div className="text-10 uppercase tracking-tightest2" style={{ color: "rgba(255,255,255,0.5)" }}>
                    Logistics · Transportation
                  </div>
                </div>
                <h2 className="font-serif leading-none" style={{ fontSize: 36, color: "white" }}>Routara<span style={{ color: ACCENT }}>.</span></h2>
                <p className="text-sm italic font-serif mt-2" style={{ color: "rgba(255,255,255,0.6)" }}>
                  Every parcel, tracked end to end.
                </p>
              </div>
            </div>

            <div className="rounded-2xl border p-5"
              style={{ background: "rgba(255,255,255,0.015)", borderColor: "rgba(255,255,255,0.06)" }}>
              <div className="text-10 uppercase tracking-tightest2 mb-3" style={{ color: "rgba(255,255,255,0.4)" }}>What I can help with</div>
              <div className="space-y-2.5">
                {[
                  "Live shipment tracking with full timeline",
                  "Instant rate quotes with cost breakdown",
                  "Schedule pickups from saved addresses",
                  "Fleet & warehouse operations status",
                  "Customs estimates for international freight",
                  "File and track delivery claims",
                ].map((t, i) => (
                  <div key={i} className="flex items-start gap-2.5">
                    <div className="rounded-full flex items-center justify-center flex-shrink-0"
                      style={{ width: 16, height: 16, background: ACCENT + "22", marginTop: 2 }}>
                      <CheckCircle2 size={9} style={{ color: ACCENT }} />
                    </div>
                    <div className="text-xs leading-relaxed" style={{ color: "rgba(255,255,255,0.75)" }}>{t}</div>
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-2xl border p-5"
              style={{ background: "rgba(255,255,255,0.015)", borderColor: "rgba(255,255,255,0.06)" }}>
              <div className="text-10 uppercase tracking-tightest2 mb-3" style={{ color: "rgba(255,255,255,0.4)" }}>Shipment screening</div>
              <div className="space-y-2.5">
                {[
                  "Blocks prohibited & dangerous goods",
                  "Flags customs-misdeclaration attempts",
                  "Protects other people's address data",
                  "Refuses prompt-injection attempts",
                ].map((t, i) => (
                  <div key={i} className="flex items-start gap-2.5">
                    <div className="rounded-full flex items-center justify-center flex-shrink-0"
                      style={{ width: 16, height: 16, background: "rgba(248,113,113,0.2)", marginTop: 2 }}>
                      <ShieldAlert size={9} style={{ color: "#fca5a5" }} />
                    </div>
                    <div className="text-xs leading-relaxed" style={{ color: "rgba(255,255,255,0.75)" }}>{t}</div>
                  </div>
                ))}
              </div>
              <div className="mt-4 pt-4 border-t flex items-center gap-2 text-10"
                style={{ borderColor: "rgba(255,255,255,0.06)", color: "rgba(255,255,255,0.5)" }}>
                <Navigation size={11} style={{ color: ACCENT }} />
                Demo only — fictional shipments & network data
              </div>
            </div>
          </aside>
        </div>

        <footer className="mt-10 pt-6 border-t flex items-center justify-between text-11"
          style={{ borderColor: "rgba(255,255,255,0.05)", color: "rgba(255,255,255,0.3)" }}>
          <div>Every parcel, tracked end to end.</div>
          <div className="italic font-serif">A conversational AI logistics demo.</div>
        </footer>
      </div>
    </div>
  );
}
