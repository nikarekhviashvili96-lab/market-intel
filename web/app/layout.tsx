import type { Metadata, Viewport } from "next";
import ThemeToggle from "./components/ThemeToggle";
import { SITE_NAME } from "@/lib/site";
import "./globals.css";

export const metadata: Metadata = {
  title: SITE_NAME,
  description: "Market and economic data with its sources.",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
};

// Sets light or dark before the first paint: the visitor's saved choice, else the phone's setting.
const themeScript = `(function(){try{var t=localStorage.getItem("theme");}catch(e){}
if(t!=="light"&&t!=="dark"){t=window.matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light";}
document.documentElement.dataset.theme=t;})();`;

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" suppressHydrationWarning className="h-full antialiased">
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
      </head>
      <body className="min-h-full">
        <div className="mx-auto flex w-full max-w-xl flex-col gap-4 px-4 py-4">
          <div className="flex items-center justify-between">
            <span className="text-base font-semibold">{SITE_NAME}</span>
            <ThemeToggle />
          </div>
          {children}
        </div>
      </body>
    </html>
  );
}
