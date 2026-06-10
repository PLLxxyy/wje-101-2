import request from "@/utils/request";
import type { ApiResponse } from "@/types/api";
import type { AuthToken, User, UserProfile } from "@/types/user";

export interface RegisterPayload {
  username: string;
  email: string;
  password: string;
  avatar: string | null;
  bio: string | null;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface UserUpdatePayload {
  username?: string;
  avatar?: string | null;
  bio?: string | null;
}

export async function registerUser(payload: RegisterPayload): Promise<User> {
  const response = await request.post<unknown, ApiResponse<User>>("/auth/register", payload);
  return response.data;
}

export async function loginUser(payload: LoginPayload): Promise<AuthToken> {
  const response = await request.post<unknown, ApiResponse<AuthToken>>("/auth/login", payload);
  return response.data;
}

export async function refreshToken(refreshTokenValue: string): Promise<AuthToken> {
  const response = await request.post<unknown, ApiResponse<AuthToken>>("/auth/refresh", {
    refresh_token: refreshTokenValue
  });
  return response.data;
}

export async function getCurrentUser(): Promise<User> {
  const response = await request.get<unknown, ApiResponse<User>>("/users/me");
  return response.data;
}

export async function getUserProfile(userId: number): Promise<UserProfile> {
  const response = await request.get<unknown, ApiResponse<UserProfile>>(`/users/${userId}`);
  return response.data;
}

export async function updateUser(userId: number, payload: UserUpdatePayload): Promise<User> {
  const response = await request.put<unknown, ApiResponse<User>>(`/users/${userId}`, payload);
  return response.data;
}

export async function followUser(userId: number): Promise<{ following: boolean }> {
  const response = await request.post<unknown, ApiResponse<{ following: boolean }>>(`/users/${userId}/follow`);
  return response.data;
}

export async function unfollowUser(userId: number): Promise<{ following: boolean }> {
  const response = await request.delete<unknown, ApiResponse<{ following: boolean }>>(`/users/${userId}/follow`);
  return response.data;
}

