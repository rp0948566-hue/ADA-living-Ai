import { listen } from "@tauri-apps/api/event";
import { invoke } from "@tauri-apps/api/core";

const LABEL: Record<string, string> = { idle: "Idle", listening: "Listening", thinking: "Thinking", speaking: "Speaking", acting: "Working", error: "Something failed" };
const notch = document.getElementById("notch")!;
const say = document.getElementById("say")!;
let hideT: number | undefined;

function setState(s: string) {
  clearTimeout(hideT);
  notch.dataset.s = s;
  document.getElementById("status")!.textContent = LABEL[s] ?? s;
  if (s === "idle") {
    hideT = window.setTimeout(() => {
      notch.classList.remove("show", "talk");
      setTimeout(() => invoke("hide_notch"), 650);   // let the retract animation finish before the window goes away
    }, 1800);
  } else notch.classList.add("show");
}
function speak(who: string, text: string, append = false) {
  if (append && say.firstElementChild?.textContent === who) { say.lastChild!.textContent += " " + text; return; }
  say.innerHTML = ""; const b = document.createElement("b"); b.textContent = who; say.append(b, document.createTextNode(text));
  notch.classList.add("show", "talk");
}
listen<{ kind: string; state?: string; text?: string }>("jeb-event", ({ payload: e }) => {
  if (e.kind === "state" && e.state) setState(e.state);
  else if (e.kind === "user" && e.text) speak("You", e.text);
  else if (e.kind === "jeb" && e.text) speak("Jeb", e.text, true);
});
