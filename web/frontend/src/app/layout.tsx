import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Sales Coach Live",
  description: "Sistema de coaching de ventas en tiempo real",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
