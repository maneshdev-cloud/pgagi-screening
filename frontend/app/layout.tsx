import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Role-Based Candidate Screening",
  description: "AI-powered screening: resume parsing, RAG-grounded questions, structured summaries.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
