import React from 'react';

export const metadata = {
  title: 'Dashboard - FinAnalytix',
  description: 'Financial Analytics Dashboard',
};

export default function DashboardRootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="dashboard-layout">
      {children}
    </div>
  );
}
