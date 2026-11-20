"use client";

// Light / dark switch. The choice is kept in this browser only; without one the page follows the phone's setting.
// The inline script in layout.tsx sets the theme before the first paint, so there is no flash.
import { useSyncExternalStore } from "react";

type Theme = "light" | "dark";

function currentTheme(): Theme {
  return document.documentElement.dataset.theme === "dark" ? "dark" : "light";
}

function subscribe(onChange: () => void) {
  const observer = new MutationObserver(onChange);
  observer.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
  return () => observer.disconnect();
}

export default function ThemeToggle() {
  const theme = useSyncExternalStore<Theme>(subscribe, currentTheme, () => "light");
  const next: Theme = theme === "dark" ? "light" : "dark";

  function toggle() {
    document.documentElement.dataset.theme = next;
    try {
      localStorage.setItem("theme", next);
    } catch {
      // storage blocked (private window): the switch still works for this visit
    }
  }

  return (
    <button
      type="button"
      onClick={toggle}
      aria-label={`Switch to ${next} mode`}
      className="min-h-11 min-w-11 rounded-md border border-line px-3 text-sm"
    >
      {theme === "dark" ? "Light" : "Dark"}
    </button>
  );
}
