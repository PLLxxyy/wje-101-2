import request from "@/utils/request";
import type { ApiResponse } from "@/types/api";
import type { BeanPayload, CoffeeBean } from "@/types/bean";

export interface BeanListParams {
  origin?: string;
  process?: string;
  flavor?: string;
  search?: string;
}

export async function listBeans(params: BeanListParams = {}): Promise<CoffeeBean[]> {
  const response = await request.get<unknown, ApiResponse<CoffeeBean[]>>("/beans", { params });
  return response.data;
}

export async function getBean(beanId: number): Promise<CoffeeBean> {
  const response = await request.get<unknown, ApiResponse<CoffeeBean>>(`/beans/${beanId}`);
  return response.data;
}

export async function createBean(payload: BeanPayload): Promise<CoffeeBean> {
  const response = await request.post<unknown, ApiResponse<CoffeeBean>>("/beans", payload);
  return response.data;
}

export async function updateBean(beanId: number, payload: Partial<BeanPayload>): Promise<CoffeeBean> {
  const response = await request.put<unknown, ApiResponse<CoffeeBean>>(`/beans/${beanId}`, payload);
  return response.data;
}

export async function deleteBean(beanId: number): Promise<boolean> {
  const response = await request.delete<unknown, ApiResponse<boolean>>(`/beans/${beanId}`);
  return response.data;
}

