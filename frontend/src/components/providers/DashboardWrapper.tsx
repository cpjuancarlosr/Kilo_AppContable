'use client';

import React from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';

interface DashboardWrapperProps {
  children: React.ReactNode;
  title: string;
}

export function DashboardWrapper({ children, title }: DashboardWrapperProps) {
  return (
    <DashboardLayout title={title}>
      {children}
    </DashboardLayout>
  );
}
