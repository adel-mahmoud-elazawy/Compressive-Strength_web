import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Concrete Compressive Strength Predictor | ML Mix Assessment",
  description:
    "Civil and materials engineering platform predicting concrete compressive strength (MPa) and structural quality classification using machine learning.",
  keywords: [
    "concrete strength",
    "compressive strength",
    "civil engineering",
    "mix design",
    "machine learning",
    "fastapi",
    "nextjs",
  ],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full">
      <body className="min-h-full bg-slate-100/70 text-slate-900 antialiased font-sans">
        {children}
      </body>
    </html>
  );
}
