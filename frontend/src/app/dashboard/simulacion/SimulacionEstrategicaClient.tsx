'use client';

import React, { useState } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Alert } from '@/components/ui/Alert';
import { Badge } from '@/components/ui/Badge';
import { formatCurrency, formatPercentage, formatNumber } from '@/lib/utils';
import { 
  TrendingUp, 
  DollarSign, 
  Calculator,
  Building2,
  ArrowRight,
  CheckCircle2,
  XCircle
} from 'lucide-react';

// Mock de resultados de simulación
const mockGrowthSimulation = {
  summary: {
    total_projected_revenue: 3150000,
    total_projected_net_income: 495000,
    average_net_margin: 0.157,
    final_month_revenue: 298000,
    final_month_net_income: 46800
  },
  monthly_projections: [
    { month: 1, revenue: 200000, expenses: 150000, ebitda: 50000, net_income: 35000 },
    { month: 2, revenue: 203000, expenses: 152000, ebitda: 51000, net_income: 35700 },
    { month: 3, revenue: 206000, expenses: 154000, ebitda: 52000, net_income: 36400 },
    { month: 4, revenue: 209000, expenses: 156000, ebitda: 53000, net_income: 37100 },
    { month: 5, revenue: 212000, expenses: 158000, ebitda: 54000, net_income: 37800 },
    { month: 6, revenue: 215000, expenses: 160000, ebitda: 55000, net_income: 38500 },
  ]
};

const mockPricingSimulation = {
  price_change_pct: 0.10,
  volume_change_pct: -0.05,
  base_scenario: {
    monthly_revenue: 200000,
    monthly_expenses: 150000,
    monthly_ebitda: 50000,
    annual_ebitda: 600000
  },
  new_scenario: {
    monthly_revenue: 209000,
    monthly_expenses: 145500,
    monthly_ebitda: 63500,
    annual_ebitda: 762000
  },
  impact: {
    monthly_ebitda_change: 13500,
    annual_ebitda_change: 162000,
    ebitda_change_pct: 0.27
  }
};

const mockFinancingSimulation = {
  financing_details: {
    amount: 500000,
    annual_rate: 0.12,
    term_months: 36,
    monthly_payment: 16607,
    total_interest: 97852
  },
  impact: {
    monthly_flow_change: -6607,
    dscr_current: 3.2,
    dscr_new: 1.8
  }
};

export function SimulacionEstrategicaClient() {
  const [activeTab, setActiveTab] = useState<'growth' | 'pricing' | 'financing'>('growth');
  
  // Form states
  const [growthRate, setGrowthRate] = useState(20);
  const [priceChange, setPriceChange] = useState(10);
  const [volumeChange, setVolumeChange] = useState(-5);
  const [financingAmount, setFinancingAmount] = useState(500000);
  const [interestRate, setInterestRate] = useState(12);

  return (
    <DashboardLayout title="Simulación Estratégica">
      {/* Tabs */}
      <div className="flex gap-2 mb-6">
        <Button
          variant={activeTab === 'growth' ? 'primary' : 'secondary'}
          onClick={() => setActiveTab('growth')}
        >
          <TrendingUp className="w-4 h-4 mr-2" />
          Crecimiento
        </Button>
        <Button
          variant={activeTab === 'pricing' ? 'primary' : 'secondary'}
          onClick={() => setActiveTab('pricing')}
        >
          <DollarSign className="w-4 h-4 mr-2" />
          Precios
        </Button>
        <Button
          variant={activeTab === 'financing' ? 'primary' : 'secondary'}
          onClick={() => setActiveTab('financing')}
        >
          <Building2 className="w-4 h-4 mr-2" />
          Financiamiento
        </Button>
      </div>

      {/* Growth Simulation */}
      {activeTab === 'growth' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Parameters */}
          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle>Parámetros</CardTitle>
              <CardDescription>Configure el escenario de crecimiento</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Input
                label="Ingresos Base Mensual"
                type="number"
                defaultValue={200000}
              />
              <Input
                label="Gastos Base Mensual"
                type="number"
                defaultValue={150000}
              />
              <Input
                label="Tasa de Crecimiento Anual (%)"
                type="number"
                value={growthRate}
                onChange={(e) => setGrowthRate(Number(e.target.value))}
              />
              <Input
                label="Meses a Proyectar"
                type="number"
                defaultValue={12}
              />
              <Button className="w-full">
                <Calculator className="w-4 h-4 mr-2" />
                Simular
              </Button>
            </CardContent>
          </Card>

          {/* Results */}
          <div className="lg:col-span-2 space-y-6">
            {/* Summary Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Card>
                <CardContent className="pt-4">
                  <p className="text-xs text-gray-500">Ingresos Proyectados</p>
                  <p className="text-lg font-bold">{formatCurrency(mockGrowthSimulation.summary.total_projected_revenue)}</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-4">
                  <p className="text-xs text-gray-500">Utilidad Neta Total</p>
                  <p className="text-lg font-bold">{formatCurrency(mockGrowthSimulation.summary.total_projected_net_income)}</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-4">
                  <p className="text-xs text-gray-500">Margen Promedio</p>
                  <p className="text-lg font-bold">{formatPercentage(mockGrowthSimulation.summary.average_net_margin * 100)}</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-4">
                  <p className="text-xs text-gray-500">Ingreso Mes 12</p>
                  <p className="text-lg font-bold">{formatCurrency(mockGrowthSimulation.summary.final_month_revenue)}</p>
                </CardContent>
              </Card>
            </div>

            {/* Monthly Projections */}
            <Card>
              <CardHeader>
                <CardTitle>Proyección Mensual</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm font-medium text-gray-700 border-b pb-2">
                    <span>Mes</span>
                    <span>Ingresos</span>
                    <span>Gastos</span>
                    <span>EBITDA</span>
                    <span>Neto</span>
                  </div>
                  {mockGrowthSimulation.monthly_projections.map((p) => (
                    <div key={p.month} className="flex justify-between text-sm py-2 border-b border-gray-100">
                      <span className="text-gray-500">{p.month}</span>
                      <span>{formatCurrency(p.revenue)}</span>
                      <span>{formatCurrency(p.expenses)}</span>
                      <span className="font-medium">{formatCurrency(p.ebitda)}</span>
                      <span className="font-medium text-green-600">{formatCurrency(p.net_income)}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {/* Pricing Simulation */}
      {activeTab === 'pricing' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Simulador de Precios</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Input
                label="Ingresos Base Mensual"
                type="number"
                defaultValue={200000}
              />
              <Input
                label="Gastos Base Mensual"
                type="number"
                defaultValue={150000}
              />
              <Input
                label="Cambio en Precio (%)"
                type="number"
                value={priceChange}
                onChange={(e) => setPriceChange(Number(e.target.value))}
              />
              <Input
                label="Cambio Esperado en Volumen (%)"
                type="number"
                value={volumeChange}
                onChange={(e) => setVolumeChange(Number(e.target.value))}
              />
              <Button className="w-full">
                <Calculator className="w-4 h-4 mr-2" />
                Calcular Impacto
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Resultado del Análisis</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-500">Escenario Base</p>
                    <p className="text-xl font-bold">{formatCurrency(mockPricingSimulation.base_scenario.annual_ebitda)}</p>
                    <p className="text-xs text-gray-400">EBITDA anual</p>
                  </div>
                  <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                    <p className="text-sm text-green-700">Nuevo Escenario</p>
                    <p className="text-xl font-bold text-green-700">{formatCurrency(mockPricingSimulation.new_scenario.annual_ebitda)}</p>
                    <p className="text-xs text-green-600">EBITDA anual</p>
                  </div>
                </div>

                <div className="p-4 bg-blue-50 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium text-blue-900">Impacto en EBITDA</span>
                    <Badge variant="success">+{formatPercentage(mockPricingSimulation.impact.ebitda_change_pct * 100)}</Badge>
                  </div>
                  <p className="text-2xl font-bold text-blue-900">
                    +{formatCurrency(mockPricingSimulation.impact.annual_ebitda_change)}
                  </p>
                  <p className="text-sm text-blue-700 mt-1">
                    Incremento anual por el ajuste de precios
                  </p>
                </div>

                <Alert type="info">
                  Considerando un aumento del {priceChange}% en precios y una reducción del {Math.abs(volumeChange)}% en volumen,
                  el impacto neto es positivo para la rentabilidad.
                </Alert>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Financing Simulation */}
      {activeTab === 'financing' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Simulador de Financiamiento</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Input
                label="Ingresos Actuales Mensuales"
                type="number"
                defaultValue={200000}
              />
              <Input
                label="Gastos Actuales Mensuales"
                type="number"
                defaultValue={150000}
              />
              <Input
                label="Deuda Actual"
                type="number"
                defaultValue={0}
              />
              <Input
                label="Nuevo Financiamiento"
                type="number"
                value={financingAmount}
                onChange={(e) => setFinancingAmount(Number(e.target.value))}
              />
              <Input
                label="Tasa de Interés Anual (%)"
                type="number"
                value={interestRate}
                onChange={(e) => setInterestRate(Number(e.target.value))}
              />
              <Input
                label="Plazo (meses)"
                type="number"
                defaultValue={36}
              />
              <Button className="w-full">
                <Calculator className="w-4 h-4 mr-2" />
                Analizar Impacto
              </Button>
            </CardContent>
          </Card>

          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Detalles del Crédito</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between py-2 border-b">
                    <span className="text-gray-600">Monto</span>
                    <span className="font-semibold">{formatCurrency(mockFinancingSimulation.financing_details.amount)}</span>
                  </div>
                  <div className="flex justify-between py-2 border-b">
                    <span className="text-gray-600">Tasa Anual</span>
                    <span className="font-semibold">{formatPercentage(mockFinancingSimulation.financing_details.annual_rate * 100)}</span>
                  </div>
                  <div className="flex justify-between py-2 border-b">
                    <span className="text-gray-600">Plazo</span>
                    <span className="font-semibold">{mockFinancingSimulation.financing_details.term_months} meses</span>
                  </div>
                  <div className="flex justify-between py-2 border-b">
                    <span className="text-gray-600">Pago Mensual</span>
                    <span className="font-semibold text-lg">{formatCurrency(mockFinancingSimulation.financing_details.monthly_payment)}</span>
                  </div>
                  <div className="flex justify-between py-2">
                    <span className="text-gray-600">Interés Total</span>
                    <span className="font-semibold">{formatCurrency(mockFinancingSimulation.financing_details.total_interest)}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Capacidad de Pago (DSCR)</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">DSCR Actual</span>
                    <Badge variant="success">{formatNumber(mockFinancingSimulation.impact.dscr_current, 1)}x</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">DSCR con Nueva Deuda</span>
                    <Badge variant={mockFinancingSimulation.impact.dscr_new >= 1.5 ? 'success' : 'warning'}>
                      {formatNumber(mockFinancingSimulation.impact.dscr_new, 1)}x
                    </Badge>
                  </div>
                  <p className="text-sm text-gray-600">
                    Se recomienda mantener el DSCR por encima de 1.5x para asegurar capacidad de pago.
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      )}
    </DashboardLayout>
  );
}
