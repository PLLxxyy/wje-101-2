import axios, { type AxiosError, type AxiosResponse, type InternalAxiosRequestConfig } from "axios";
import { ElMessage } from "element-plus";

import type { ApiError, ApiResponse } from "@/types/api";
import type { AuthToken } from "@/types/user";
import { clearTokens, getAccessToken, getRefreshToken, setTokens } from "@/utils/storage";

interface RetriableConfig extends InternalAxiosRequestConfig {
  _retry?: boolean;
}

const request = axios.create({
  baseURL: "/api",
  timeout: 15000
});

let refreshing: Promise<string | null> | null = null;

request.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers.set("Authorization", `Bearer ${token}`);
  }
  return config;
});

request.interceptors.response.use(
  ((response: AxiosResponse<ApiResponse<unknown>>) => {
    const payload = response.data as ApiResponse<unknown>;
    if (payload.code !== 0) {
      const apiError: ApiError = { code: payload.code, message: payload.message, data: null };
      throw apiError;
    }
    return payload;
  }) as unknown as (value: AxiosResponse) => AxiosResponse | Promise<AxiosResponse>,
  async (error: AxiosError<ApiError>) => {
    const config = error.config as RetriableConfig | undefined;
    if (error.response?.status === 401 && config && !config._retry) {
      config._retry = true;
      const token = await refreshAccessToken();
      if (token) {
        config.headers.set("Authorization", `Bearer ${token}`);
        return request(config);
      }
    }
    const message = error.response?.data?.message || error.message || "请求失败";
    ElMessage.error(message);
    if (error.response?.status === 401) {
      clearTokens();
    }
    return Promise.reject(error);
  }
);

async function refreshAccessToken(): Promise<string | null> {
  if (refreshing) {
    return refreshing;
  }
  refreshing = performRefresh();
  const token = await refreshing;
  refreshing = null;
  return token;
}

async function performRefresh(): Promise<string | null> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) {
    return null;
  }
  try {
    const response = await axios.post<ApiResponse<AuthToken>>("/api/auth/refresh", {
      refresh_token: refreshToken
    });
    if (response.data.code !== 0) {
      return null;
    }
    setTokens(response.data.data.access_token, response.data.data.refresh_token);
    return response.data.data.access_token;
  } catch {
    clearTokens();
    return null;
  }
}

export default request;
