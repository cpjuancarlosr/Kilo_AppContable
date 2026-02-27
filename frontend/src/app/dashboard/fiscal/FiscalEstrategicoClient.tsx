'use client';

import React, { useState } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Alert } from '@/components/ui/Alert';
import { Badge } from '@/components/ui/Badge';
import { formatCurrency, formatPercentage } from '@/lib/utils';
import { AlertTriangle, TrendingUp, TrendingDown, Calculator } from 'lucide-react';

// Mock de datos fiscales
const mockTaxSummary = {
  revenue: 2450000,
  taxable_income: 385000,
  income_tax: 115500,
  vat_collected: 392000,
  vat_paid: 224000,
  vat_net: 168000,
  other_taxes: 15000,
  total_tax: 298500,
  effective_tax_rate: 12.18
};

const mockTaxProjection = [
  { month: 1, projected_revenue: 210000, projected_taxable_income: 33000, projected_income_tax: 9900, projected_vat: 33600, projected_total_tax: 43500, cumulative_tax: 43500 },
  { month: 2, projected_revenue: 220500, projected_taxable_income: 34650, projected_income_tax: 10395, projected_vat: 35280, projected_total_tax: 45675, cumulative_tax: 89175 },
  { month: 3, projected_revenue: 231525, projected_taxable_income: 36383, projected_income_tax: 10915, projected_vat: 37044, projected_total_tax: 47959, cumulative_tax: 137134 },
  { month: 4, projected_revenue: 243101, projected_taxable_income: 38202, projected_income_tax: 11461, projected_vat: 38896, projected_total_tax: 50357, cumulative_tax: 187491 },
  { month: 5, projected_revenue: 255256, projected_taxable_income: 40112, projected_income_tax: 12034, projected_vat: 40841, projected_total_tax: 52875, cumulative_tax: 240366 },
  { month: 6, projected_revenue: 268019, projected_taxable_income: 42118, projected_income_tax: 12635, projected_vat: 42883, projected_total_tax: 55518, cumulative_tax: 295884 },
];

const mockRiskAssessment = {
  risk_level: 'medium',
  total_score: 6,
  factors: [
    { factor: 'Deducciones Documentadas', risk_level: 'low', score: 2 },
    { factor: 'Retenciones de ISR', risk_level: 'medium', score: 3 },
    { factor: 'Declaraciones Oportunas', risk_level: 'low', score: 1 }
  ],
  recommendations: [
    'Verificar documentación de gastos de representación',
    'Actualizar tablas de retención de ISR',
    'Revisar cálculo de pagos provisionales'
  ]
};

export function FiscalEstrategicoClient() {
  const [baseRevenue, setBaseRevenue] = useState(200000);
  const [growthRate, setGrowthRate] = useState(5);
  const [projectionMonths, setProjectionMonths] = useState(12);

  const totalProjectedTax = mockTaxProjection[mockTaxProjection.length - 1]?.cumulative_tax || 0;
  const avgMonthlyTax = totalProjectedTax / mockTaxProjection.length;

  return (
    <DashboardLayout title="Fiscal Estratégico">
      {/* Resumen Fiscal */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-gray-500">ISR Pagado</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">
              {formatCurrency(mockTaxSummary.income_tax)}
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-gray-500">IVA Neto</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">
              {formatCurrency(mockTaxSummary.vat_net)}
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-gray-500">Carga Total</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">
              {formatCurrency(mockTaxSummary.total_tax)}
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-gray-500">Tasa Efectiva</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">
              {formatPercentage(mockTaxSummary.effective_tax_rate)}
            </p>
            <Badge variant={mockTaxSummary.effective_tax_rate < 15 ? 'success' : 'warning'} className="mt-2">
              {mockTaxSummary.effective_tax_rate < 15 ? 'Óptima' : 'Revisar'}
            </Badge>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Proyección Fiscal */}
        <Card>
          <CardHeader>
            <CardTitle>Proyección Fiscal (6 meses)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg">
                <div>
                  <p className="text-sm text-gray-500">Impuesto Proyectado</p>
                  <p className="text-xl font-bold text-gray-900">
                    {formatCurrency(totalProjectedTax)}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Promedio Mensual</p>
                  <p className="text-xl font-bold text-gray-900">
                    {formatCurrency(avgMonthlyTax)}
                  </p>
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex justify-between text-sm font-medium text-gray-700 border-b pb-2">
                  <span>Mes</span>
                  <span>Ingreso</span>
                  <span>ISR</span>
                  <span>Total</span>
                </div>
                {mockTaxProjection.map((p) => (
                  <div key={p.month} className="flex justify-between text-sm py-2 border-b border-gray-100">
                    <span className="text-gray-500">Mes {p.month}</span>
                    <span>{formatCurrency(p.projected_revenue)}</span>
                    <span>{formatCurrency(p.projected_income_tax)}</span>
                    <span className="font-medium">{formatCurrency(p.projected_total_tax)}</span>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Evaluación de Riesgo */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="w-5 h-5" />
                Evaluación de Riesgo Fiscal
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-4 mb-6">
                <div className={`text-4xl font-bold ${
                  mockRiskAssessment.risk_level === 'low' ? 'text-green-600' :
                  mockRiskAssessment.risk_level === 'medium' ? 'text-yellow-600' : 'text-red-600'
                }`}>
                  {mockRiskAssessment.total_score}/10
                </div>
                <div>
                  <p className="font-semibold text-gray-900">Nivel de Riesgo</p>
                  <Badge variant={
                    mockRiskAssessment.risk_level === 'low' ? 'success' :
                    mockRiskAssessment.risk_level === 'medium' ? 'warning' : 'danger'
                  }>
                    {mockRiskAssessment.risk_level === 'low' ? 'BAJO' :
                     mockRiskAssessment.risk_level === 'medium' ? 'MEDIO' : 'ALTO'}
                  </Badge>
                </div>
              </div>

              <div className="space-y-3">
                {mockRiskAssessment.factors.map((factor, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <span className="text-sm text-gray-700">{factor.factor}</span>
                    <Badge variant={
                      factor.risk_level === 'low' ? 'success' :
                      factor.risk_level === 'medium' ? 'warning' : 'danger'
                    }>
                      {factor.score} pts
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {mockRiskAssessment.recommendations.length > 0 && (
            <Alert type="warning" title="Recomendaciones">
              <ul className="list-disc list-inside space-y-1">
                {mockRiskAssessment.recommendations.map((rec, idx) => (
                  <li key={idx}>{rec}</li>
                ))}
              </ul>
            </Alert>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
