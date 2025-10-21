import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "RentRate - Review Rooms, Apartments, and Landlords",
  description: "A platform for tenants to review rooms, apartments, and landlords",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pl">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
