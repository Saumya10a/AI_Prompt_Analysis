import axios, { type AxiosError, type AxiosInstance } from 'axios';
import type {
  HealthEcosystemResponse,
  OverviewStats,
  CategoryAnalytics,
  ModelAnalytics,
  ReconciliationReport,
  PromptInspectionResult,
  ApiError,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

class ApiClient {
  private client: AxiosInstance;
  private isLoading = false;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 120000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        const apiError: ApiError = {
          message: error.message || 'An unexpected error occurred',
          status: error.response?.status,
        };

        if (error.response?.data) {
          apiError.message = (error.response.data as any).detail || apiError.message;
        }

        return Promise.reject(apiError);
      }
    );
  }

  private async request<T>(requestFn: () => Promise<T>): Promise<T> {
    this.isLoading = true;
    try {
      return await requestFn();
    } finally {
      this.isLoading = false;
    }
  }

  getGlobalLoadingState(): boolean {
    return this.isLoading;
  }

  async getHealthEcosystem(): Promise<HealthEcosystemResponse> {
    return this.request(async () => {
      const response = await this.client.get<HealthEcosystemResponse>('/v1/health-ecosystem');
      return this.validateResponse(response.data, 'HealthEcosystemResponse');
    });
  }

  async getOverviewAnalytics(): Promise<OverviewStats> {
    return this.request(async () => {
      const response = await this.client.get<OverviewStats>('/v1/analytics/overview');
      return this.validateResponse(response.data, 'OverviewStats');
    });
  }

  async getCategoryAnalytics(): Promise<CategoryAnalytics[]> {
    return this.request(async () => {
      const response = await this.client.get<CategoryAnalytics[]>('/v1/analytics/categories');
      return this.validateArrayResponse(response.data, 'CategoryAnalytics');
    });
  }

  async getModelAnalytics(): Promise<ModelAnalytics[]> {
    return this.request(async () => {
      const response = await this.client.get<ModelAnalytics[]>('/v1/analytics/models');
      return this.validateArrayResponse(response.data, 'ModelAnalytics');
    });
  }

  async getReconciliationReports(): Promise<ReconciliationReport[]> {
    return this.request(async () => {
      const response = await this.client.get<ReconciliationReport[]>('/v1/analytics/reconciliation');
      return this.validateArrayResponse(response.data, 'ReconciliationReport');
    });
  }

  async inspectPrompt(prompt: string): Promise<PromptInspectionResult> {
    return this.request(async () => {
      const response = await this.client.post<PromptInspectionResult>('/v1/prompt/inspect', {
        prompt,
      });
      return this.validateResponse(response.data, 'PromptInspectionResult');
    });
  }

  private validateResponse<T>(data: unknown, typeName: string): T {
    if (!data || typeof data !== 'object') {
      throw new Error(`Invalid ${typeName} response: expected object, received ${typeof data}`);
    }
    return data as T;
  }

  private validateArrayResponse<T>(data: unknown, typeName: string): T[] {
    if (!Array.isArray(data)) {
      throw new Error(`Invalid ${typeName} response: expected array, received ${typeof data}`);
    }
    return data as T[];
  }
}

export const apiClient = new ApiClient();
