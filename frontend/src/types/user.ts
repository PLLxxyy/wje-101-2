import type { UserRole } from "./enums";

export interface User {
  id: number;
  username: string;
  email: string;
  avatar: string | null;
  bio: string | null;
  role: UserRole;
  created_at: string;
}

export interface UserStats {
  note_count: number;
  average_score: number;
  top_origins: string[];
  radar_scores: {
    aroma: number;
    acidity: number;
    body: number;
    overall: number;
  };
  following_count: number;
  follower_count: number;
  is_following: boolean;
}

export interface UserProfile {
  user: User;
  stats: UserStats;
}

export interface AuthToken {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

