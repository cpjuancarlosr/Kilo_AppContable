'use client';

import React, { useState, useEffect } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { MetricCard } from '@/components/ui/MetricCard';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Alert } from '@/components/ui/Alert';
import { Badge } from '@/components/ui/Badge';
import { 
  DollarSign, 
  TrendingUp, 
  PiggyBank, 
  CreditCard,
  Activity,
  AlertTriangle,
  ArrowUpRight,
  ArrowDownRight
} from 'lucide-react';
import { executiveApi } from '@/lib/api';
import { formatCurrency, formatPercentage } from '@/lib/utils';

// Datos de ejemplo para demo
const mockData = {
  revenue_current: 2450000,
  revenue_previous: 2100000,
  revenue_change_pct: 16.7,
  net_income_current: 385000,
  net_income_previous: 320000,
  net_income_change_pct: 20.3,
  ebitda_current: 612500,
  ebitda_margin_pct: 25.0,
  cash_balance: 485000,
  cash_runway_months: 8.5,
  accounts_receivable: 320000,
  accounts_payable: 185000,
  working_capital: 420000,
  alerts: [
    {
      type: 'warning' as const,
      title: 'Efectivo Bajo',
      message: 'El efectivo disponible representa menos de 3 meses de operaciones.'
    },
    {
      type: 'info' as const,
      title: 'Crecimiento Sostenido',
      message: 'Los ingresos han crecido un 16.7% comparado con el año anterior.'
    }
  ]
};

type DashboardData = typeof mockData;

export default function ExecutiveDashboard() {
  const [data, setData] = useState<DashboardData>(mockData);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // En producción, llamar a la API real
    // fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const response = await executiveApi.getMetrics('company-uuid');
      setData(response as DashboardData);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardLayout title="Dashboard Ejecutivo">
      {/* KPIs Principales */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <MetricCard
          title="Ingresos (YTD)"
          value={data.revenue_current}
          change={data.revenue_change_pct}
          changeLabel="vs año anterior"
          trend={data.revenue_change_pct > 0 ? 'up' : 'down'}
          isCurrency
          icon={<DollarSign className="w-6 h-6 text-gray-600" />}
        />
        
        <MetricCard
          title="Utilidad Neta"
          value={data.net_income_current}
          change={data.net_income_change_pct}
          changeLabel="vs año anterior"
          trend={data.net_income_change_pct > 0 ? 'up' : 'down'}
          isCurrency
          icon={<TrendingUp className="w-6 h-6 text-gray-600" />}
        />
        
        <MetricCard
          title="EBITDA"
          value={data.ebitda_current}
          subtitle={`Margen: ${formatPercentage(data.ebitda_margin_pct)}`}
          trend="up"
          isCurrency
          icon={<Activity className="w-6 h-6 text-gray-600" />}
        />
        
        <MetricCard
          title="Efectivo Disponible"
          value={data.cash_balance}
          subtitle={`Runway: ${data.cash_runway_months} meses`}
          trend={data.cash_runway_months > 6 ? 'up' : 'down'}
          isCurrency
          icon={<PiggyBank className="w-6 h-6 text-gray-600" />}
        />
      </div>

      {/* Alertas y Capital de Trabajo */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Alertas */}
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-lg font-semibold text-gray-900">Alertas Inteligentes</h2>
          {data.alerts.map((alert, index) => (
            <Alert key={index} type={alert.type} title={alert.title}>
              {alert.message}
            </Alert>
          ))}
        </div>

        {/* Capital de Trabajo */}
        <Card>
          <CardHeader>
            <CardTitle>Capital de Trabajo</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Capital de Trabajo</span>
                <span className="font-semibold text-lg">
                  {formatCurrency(data.working_capital)}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Cuentas por Cobrar</span>
                <span className="font-semibold">
                  {formatCurrency(data.accounts_receivable)}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Cuentas por Pagar</span>
                <span className="font-semibold">
                  {formatCurrency(data.accounts_payable)}
                </span>
              </div>
              <div className="pt-4 border-t border-gray-200">
                <div className="flex justify-between items-center">
                  <span className="font-medium">Ratio Liquidez</span>
                  <Badge variant="success">
                    {formatPercentage((data.working_capital + data.accounts_payable) / data.accounts_payable)}
                  </Badge>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Métricas Adicionales */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Margen Neto</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {formatPercentage((data.net_income_current / data.revenue_current) * 100)}
                </p>
              </div>
              <div className="p-3 bg-gray-100 rounded-full">
                <ArrowUpRight className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Rotación Cartera</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">45 días</p>
              </div>
              <div className="p-3 bg-gray-100 rounded-full">
                <CreditCard className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Eficiencia Operativa</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">94.2%</p>
              </div>
              <div className="p-3 bg-gray-100 rounded-full">
                <Activity className="w-6 h-6 text-purple-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
