import './globals.css';
import { ReactNode } from 'react';

export const metadata = {
  title: 'Haryana CMO Grievance Portal',
  description: 'One front door for public grievances in Haryana'
};

export default function RootLayout({children}:{children:ReactNode}) {
  return <html lang="hi"><body>{children}</body></html>;
}
