import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ThinkGym",
  description: "ThinkGym Mini Flow Demo",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}
