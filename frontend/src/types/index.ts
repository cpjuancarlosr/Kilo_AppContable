/**
 * Tipos TypeScript para FinAnalytix
 */

export interface ExecutiveMetrics {
  revenue_current: number;
  revenue_previous: number;
  revenue_change_pct: number;
  net_income_current: number;
  net_income_previous: number;
  net_income_change_pct: number;
  ebitda_current: number;
  ebitda_margin_pct: number;
  cash_balance: number;
  cash_runway_months: number | null;
  accounts_receivable: number;
  accounts_payable: number;
  working_capital: number;
  alerts: Alert[];
}

export interface Alert {
  type: 'danger' | 'warning' | 'info';
  title: string;
  message: string;
}

export interface FinancialRatio {
  name: string;
  value: number | null;
  benchmark?: number;
  status: 'good' | 'warning' | 'danger' | 'neutral';
}

export interface IncomeStatement {
  revenue: number;
  cost_of_goods_sold: number;
  gross_profit: number;
  operating_expenses: number;
  operating_income: number;
  depreciation_amortization: number;
  ebitda: number;
  financial_expenses: number;
  other_expenses: number;
  income_tax: number;
  net_income: number;
  margins: {
    gross: number;
    ebitda: number;
    operating: number;
    net: number;
  };
}

export interface CashConversionCycle {
  dso: number;
  dio: number;
  dpo: number;
  ccc: number;
}

export interface BreakEvenAnalysis {
  fixed_costs: number;
  variable_costs: number;
  contribution_margin: number;
  contribution_margin_pct: number;
  break_even_revenue: number;
  safety_margin_pct: number;
  current_revenue: number;
  break_even_units?: number;
  current_units?: number;
}

export interface VerticalAnalysisItem {
  concept: string;
  amount: number;
  percentage: number;
}

export interface HorizontalAnalysisItem {
  concept: string;
  current: number;
  previous: number;
  absolute_change: number;
  percentage_change: number;
}

export interface TaxSummary {
  revenue: number;
  taxable_income: number;
  income_tax: number;
  vat_collected: number;
  vat_paid: number;
  vat_net: number;
  other_taxes: number;
  total_tax: number;
  effective_tax_rate: number;
}

export interface ScenarioParameters {
  base_revenue: number;
  base_expenses: number;
  annual_growth_rate: number;
  months: number;
}

export interface ScenarioResult {
  month: number;
  revenue: number;
  expenses: number;
  ebitda: number;
  net_income: number;
  cumulative_revenue?: number;
  cumulative_net_income?: number;
}

export interface SimulationResult {
  scenario_type: string;
  parameters: ScenarioParameters;
  summary: {
    total_projected_revenue: number;
    total_projected_net_income: number;
    average_net_margin: number;
    final_month_revenue: number;
    final_month_net_income: number;
  };
  monthly_projections: ScenarioResult[];
}

export interface NavigationItem {
  label: string;
  href: string;
  icon: string;
  submenu?: NavigationItem[];
}
