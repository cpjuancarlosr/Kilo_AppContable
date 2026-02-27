import React from 'react';
import { ExecutiveDashboardClient } from './ExecutiveDashboardClient';

export const metadata = {
  title: 'Dashboard Ejecutivo - FinAnalytix',
  description: 'Panel ejecutivo con métricas financieras clave',
};

export default function ExecutiveDashboardPage() {
  return <ExecutiveDashboardClient />;
}
