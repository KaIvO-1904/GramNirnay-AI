import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/ui/Navbar";
import { LanguageProvider } from "@/lib/LanguageContext";
import { ThemeProvider } from "@/lib/ThemeContext";
import { AppProvider } from "@/lib/AppContext";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
  display: "swap",
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "GramNirnay.ai | Rural Business Intelligence",
  description: "AI-Driven Hyper-Local Business Advisory and Financial Structuring Assistant for Rural Micro-Entrepreneurs.",
  openGraph: {
    title: "GramNirnay.ai",
    description: "Hyper-Local Business Intelligence for Rural Micro-Entrepreneurs",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "GramNirnay.ai",
    description: "Hyper-Local Business Intelligence for Rural Micro-Entrepreneurs",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col" style={{ backgroundColor: 'var(--surface-0)', color: 'var(--text-primary)' }}>
        <ThemeProvider>
          <LanguageProvider>
            <AppProvider>
              <Navbar />
              <main className="flex-1">
                {children}
              </main>
            </AppProvider>
          </LanguageProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
