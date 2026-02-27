'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  BarChart3,
  Calculator,
  PieChart,
  Settings,
  TrendingUp,
  AlertCircle,
  FileText
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
}

const navigation = [
  {
    name: 'Dashboard Ejecutivo',
    href: '/dashboard/ejecutivo',
    icon: LayoutDashboard,
    section: 'ejecutiva'
  },
  {
    name: 'Control Financiero',
    href: '/dashboard/control',
    icon: BarChart3,
    section: 'control'
  },
  {
    name: 'Análisis Vertical',
    href: '/dashboard/control/vertical',
    icon: PieChart,
    section: 'control'
  },
  {
    name: 'Análisis Horizontal',
    href: '/dashboard/control/horizontal',
    icon: TrendingUp,
    section: 'control'
  },
  {
    name: 'Fiscal Estratégico',
    href: '/dashboard/fiscal',
    icon: Calculator,
    section: 'fiscal'
  },
  {
    name: 'Proyección Fiscal',
    href: '/dashboard/fiscal/proyeccion',
    icon: FileText,
    section: 'fiscal'
  },
  {
    name: 'Simulación',
    href: '/dashboard/simulacion',
    icon: Settings,
    section: 'simulacion'
  },
];

export function Sidebar({ isOpen }: SidebarProps) {
  const pathname = usePathname();

  return (
    <aside
      className={cn(
        'fixed left-0 top-0 z-40 h-screen w-64 bg-white border-r border-gray-200 transition-transform duration-300 ease-in-out',
        !isOpen && '-translate-x-full'
      )}
    >
      {/* Logo */}
      <div className="flex h-16 items-center border-b border-gray-200 px-6">
        <Link href="/dashboard/ejecutivo" className="flex items-center gap-2">
          <div className="w-8 h-8 bg-black rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">FA</span>
          </div>
          <span className="font-semibold text-lg text-gray-900">FinAnalytix</span>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-4">
        <div className="px-3 space-y-1">
          {/* Capa Ejecutiva */}
          <div className="mb-6">
            <p className="px-3 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
              Ejecutivo
            </p>
            {navigation.filter(n => n.section === 'ejecutiva').map((item) => (
              <NavItem key={item.href} item={item} pathname={pathname} />
            ))}
          </div>

          {/* Capa de Control */}
          <div className="mb-6">
            <p className="px-3 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
              Control Financiero
            </p>
            {navigation.filter(n => n.section === 'control').map((item) => (
              <NavItem key={item.href} item={item} pathname={pathname} />
            ))}
          </div>

          {/* Capa Fiscal */}
          <div className="mb-6">
            <p className="px-3 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
              Fiscal
            </p>
            {navigation.filter(n => n.section === 'fiscal').map((item) => (
              <NavItem key={item.href} item={item} pathname={pathname} />
            ))}
          </div>

          {/* Capa de Simulación */}
          <div className="mb-6">
            <p className="px-3 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
              Simulación
            </p>
            {navigation.filter(n => n.section === 'simulacion').map((item) => (
              <NavItem key={item.href} item={item} pathname={pathname} />
            ))}
          </div>
        </div>
      </nav>

      {/* Footer */}
      <div className="border-t border-gray-200 p-4">
        <div className="flex items-center gap-3 px-3 py-2">
          <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
            <span className="text-sm font-medium text-gray-600">US</span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 truncate">Usuario</p>
            <p className="text-xs text-gray-500 truncate">Administrador</p>
          </div>
        </div>
      </div>
    </aside>
  );
}

function NavItem({ item, pathname }: { item: typeof navigation[0]; pathname: string }) {
  const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
  const Icon = item.icon;

  return (
    <Link
      href={item.href}
      className={cn(
        'flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md transition-colors',
        isActive
          ? 'bg-black text-white'
          : 'text-gray-700 hover:bg-gray-100'
      )}
    >
      <Icon className="w-5 h-5 flex-shrink-0" />
      <span className="truncate">{item.name}</span>
    </Link>
  );
}
