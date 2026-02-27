/**
 * Cliente API para comunicación con el backend
 */

import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000,
    });

    // Interceptor para agregar token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );
  }

  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.get<T>(url, config);
    return response.data;
  }

  async post<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.post<T>(url, data, config);
    return response.data;
  }

  async put<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.put<T>(url, data, config);
    return response.data;
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.delete<T>(url, config);
    return response.data;
  }
}

export const apiClient = new ApiClient();

// Endpoints específicos
export const executiveApi = {
  getMetrics: (companyId: string, asOfDate?: string) =>
    apiClient.get(`/executive/metrics?company_id=${companyId}${asOfDate ? `&as_of_date=${asOfDate}` : ''}`),
  
  getAlerts: (companyId: string) =>
    apiClient.get(`/executive/alerts?company_id=${companyId}`),
  
  getKPIs: (companyId: string) =>
    apiClient.get(`/executive/kpis?company_id=${companyId}`),
};

export const controlApi = {
  getCompleteAnalysis: (companyId: string, startDate: string, endDate: string) =>
    apiClient.get(`/control/complete-analysis?company_id=${companyId}&start_date=${startDate}&end_date=${endDate}`),
  
  getVerticalAnalysis: (companyId: string, startDate: string, endDate: string) =>
    apiClient.get(`/control/vertical-analysis?company_id=${companyId}&start_date=${startDate}&end_date=${endDate}`),
  
  getHorizontalAnalysis: (companyId: string, startDate: string, endDate: string) =>
    apiClient.get(`/control/horizontal-analysis?company_id=${companyId}&start_date=${startDate}&end_date=${endDate}`),
  
  getRatios: (companyId: string, startDate: string, endDate: string) =>
    apiClient.get(`/control/ratios?company_id=${companyId}&start_date=${startDate}&end_date=${endDate}`),
  
  getCashConversionCycle: (companyId: string, startDate: string, endDate: string) =>
    apiClient.get(`/control/cash-conversion-cycle?company_id=${companyId}&start_date=${startDate}&end_date=${endDate}`),
  
  getBreakEven: (companyId: string, startDate: string, endDate: string) =>
    apiClient.get(`/control/break-even?company_id=${companyId}&start_date=${startDate}&end_date=${endDate}`),
};

export const fiscalApi = {
  getSummary: (companyId: string, startDate: string, endDate: string) =>
    apiClient.get(`/fiscal/summary?company_id=${companyId}&start_date=${startDate}&end_date=${endDate}`),
  
  getProjection: (companyId: string, baseRevenue: number, baseTaxableIncome: number, growthRate: number, months: number) =>
    apiClient.get(`/fiscal/projection?company_id=${companyId}&base_revenue=${baseRevenue}&base_taxable_income=${baseTaxableIncome}&growth_rate=${growthRate}&months=${months}`),
  
  getRiskAssessment: (companyId: string) =>
    apiClient.get(`/fiscal/risk-assessment?company_id=${companyId}`),
};

export const simulationApi = {
  simulateGrowth: (companyId: string, baseRevenue: number, baseExpenses: number, growthRate: number, months: number) =>
    apiClient.post(`/simulation/growth?company_id=${companyId}&base_revenue=${baseRevenue}&base_expenses=${baseExpenses}&annual_growth_rate=${growthRate}&months=${months}`),
  
  simulatePricing: (companyId: string, baseRevenue: number, baseExpenses: number, priceChange: number, volumeChange: number) =>
    apiClient.post(`/simulation/pricing?company_id=${companyId}&base_revenue=${baseRevenue}&base_expenses=${baseExpenses}&price_change_pct=${priceChange}&expected_volume_change_pct=${volumeChange}`),
  
  simulateFinancing: (companyId: string, currentRevenue: number, currentExpenses: number, currentDebt: number, newFinancing: number, interestRate: number, termMonths: number) =>
    apiClient.post(`/simulation/financing?company_id=${companyId}&current_revenue=${currentRevenue}&current_expenses=${currentExpenses}&current_debt=${currentDebt}&new_financing=${newFinancing}&interest_rate=${interestRate}&term_months=${termMonths}`),
  
  simulateExpansion: (companyId: string, currentRevenue: number, currentExpenses: number, investment: number, additionalCost: number, revenueUplift: number) =>
    apiClient.post(`/simulation/expansion?company_id=${companyId}&current_revenue=${currentRevenue}&current_expenses=${currentExpenses}&expansion_investment=${investment}&additional_monthly_cost=${additionalCost}&revenue_uplift_pct=${revenueUplift}`),
};
