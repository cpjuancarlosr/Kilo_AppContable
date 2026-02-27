'use client';

import React, { useState } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { MetricCard } from '@/components/ui/MetricCard';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Badge';
import { formatCurrency, formatPercentage, formatNumber } from '@/lib/utils';
import { 
  TrendingUp, 
  TrendingDown, 
  Calculator,
  Calendar,
  ArrowRight
} from 'lucide-react';

// Datos de ejemplo
const mockRatios = {
  current_ratio: 1.85,
  quick_ratio: 1.42,
  debt_to_equity: 0.65,
  roa: 12.5,
  roe: 18.3,
  gross_margin: 42.8,
  operating_margin: 25.0,
  net_margin: 15.7,
  asset_turnover: 0.80,
  inventory_turnover: 6.2
};

const mockBreakEven = {
  fixed_costs: 450000,
  variable_costs: 1400000,
  contribution_margin: 1050000,
  contribution_margin_pct: 0.4286,
  break_even_revenue: 1050000,
  safety_margin_pct: 57.1,
  current_revenue: 2450000
};

const mockCCC = {
  dso: 47.5,
  dio: 52.3,
  dpo: 38.2,
  ccc: 61.6
};

export function ControlFinancieroClient() {
  const [startDate, setStartDate] = useState('2024-01-01');
  const [endDate, setEndDate] = useState('2024-12-31');

  const getRatioStatus = (name: string, value: number): 'success' | 'warning' | 'danger' => {
    const benchmarks: Record<string, { good: number; warning: number }> = {
      current_ratio: { good: 1.5, warning: 1.0 },
      quick_ratio: { good: 1.0, warning: 0.8 },
      debt_to_equity: { good: 0.5, warning: 1.0 },
      roa: { good: 10, warning: 5 },
      roe: { good: 15, warning: 10 },
      gross_margin: { good: 40, warning: 25 },
      operating_margin: { good: 20, warning: 10 },
      net_margin: { good: 10, warning: 5 },
    };
    
    const benchmark = benchmarks[name];
    if (!benchmark) return 'neutral' as any;
    
    if (name === 'debt_to_equity') {
      return value < benchmark.good ? 'success' : value < benchmark.warning ? 'warning' : 'danger';
    }
    return value >= benchmark.good ? 'success' : value >= benchmark.warning ? 'warning' : 'danger';
  };

  return (
    <DashboardLayout title="Control Financiero">
      {/* Filtros de período */}
      <Card className="mb-6">
        <CardContent className="py-4">
          <div className="flex flex-wrap items-end gap-4">
            <div className="flex-1 min-w-[200px]">
              <Input
                label="Fecha Inicio"
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
            </div>
            <div className="flex-1 min-w-[200px]">
              <Input
                label="Fecha Fin"
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
            </div>
            <Button className="mb-0">
              <Calendar className="w-4 h-4 mr-2" />
              Actualizar
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Ratios Financieros */}
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Ratios Financieros</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
        {Object.entries(mockRatios).map(([key, value]) => (
          <Card key={key}>
            <CardContent className="pt-4">
              <p className="text-xs text-gray-500 uppercase tracking-wide">
                {key.replace(/_/g, ' ')}
              </p>
              <div className="flex items-center justify-between mt-2">
                <p className="text-xl font-bold text-gray-900">
                  {key.includes('margin') || ['roa', 'roe'].includes(key) 
                    ? formatPercentage(value)
                    : formatNumber(value, 2)}
                </p>
                <Badge variant={getRatioStatus(key, value)}>
                  {getRatioStatus(key, value) === 'success' ? 'Óptimo' : 
                   getRatioStatus(key, value) === 'warning' ? 'Atención' : 'Revisar'}
                </Badge>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Análisis de Punto de Equilibrio */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <Card>
          <CardHeader>
            <CardTitle>Punto de Equilibrio</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                <span className="text-gray-600">Ingresos Actuales</span>
                <span className="font-semibold text-lg">
                  {formatCurrency(mockBreakEven.current_revenue)}
                </span>
              </div>
              
              <div className="flex justify-between items-center p-3 bg-red-50 rounded-lg border border-red-100">
                <span className="text-red-700">Punto de Equilibrio</span>
                <span className="font-semibold text-lg text-red-700">
                  {formatCurrency(mockBreakEven.break_even_revenue)}
                </span>
              </div>
              
              <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg border border-green-100">
                <span className="text-green-700">Margen de Seguridad</span>
                <span className="font-semibold text-lg text-green-700">
                  {formatPercentage(mockBreakEven.safety_margin_pct * 100)}
                </span>
              </div>

              <div className="pt-4 border-t border-gray-200 space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Costos Fijos</span>
                  <span className="font-medium">{formatCurrency(mockBreakEven.fixed_costs)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Margen de Contribución</span>
                  <span className="font-medium">
                    {formatPercentage(mockBreakEven.contribution_margin_pct * 100)}
                  </span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Ciclo de Conversión de Efectivo */}
        <Card>
          <CardHeader>
            <CardTitle>Ciclo de Conversión de Efectivo</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <p className="text-2xl font-bold text-gray-900">{mockCCC.dso}</p>
                  <p className="text-xs text-gray-500 mt-1">DSO (días)</p>
                  <p className="text-xs text-gray-400">Cobro</p>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <p className="text-2xl font-bold text-gray-900">{mockCCC.dio}</p>
                  <p className="text-xs text-gray-500 mt-1">DIO (días)</p>
                  <p className="text-xs text-gray-400">Inventario</p>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <p className="text-2xl font-bold text-gray-900">{mockCCC.dpo}</p>
                  <p className="text-xs text-gray-500 mt-1">DPO (días)</p>
                  <p className="text-xs text-gray-400">Pago</p>
                </div>
              </div>

              <div className="flex items-center justify-center py-4">
                <div className="text-center">
                  <p className="text-sm text-gray-500">Ciclo Total (CCC)</p>
                  <p className="text-4xl font-bold text-gray-900">{mockCCC.ccc}</p>
                  <p className="text-sm text-gray-400">días</p>
                </div>
              </div>

              <div className="text-sm text-gray-600 bg-blue-50 p-3 rounded-lg">
                <p className="font-medium mb-1">Interpretación:</p>
                <p>Se requieren {mockCCC.ccc} días para convertir la inversión en inventario y cuentas por cobrar en efectivo.</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
