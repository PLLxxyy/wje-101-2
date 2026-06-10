export enum RoastLevel {
  Light = "light",
  Medium = "medium",
  Dark = "dark"
}

export enum UserRole {
  User = "user",
  Admin = "admin"
}

export enum ProcessMethod {
  Washed = "washed",
  Natural = "natural",
  Honey = "honey",
  Anaerobic = "anaerobic"
}

export const roastLevelLabel: Record<RoastLevel, string> = {
  [RoastLevel.Light]: "浅烘",
  [RoastLevel.Medium]: "中烘",
  [RoastLevel.Dark]: "深烘"
};

export const processMethodLabel: Record<ProcessMethod, string> = {
  [ProcessMethod.Washed]: "水洗",
  [ProcessMethod.Natural]: "日晒",
  [ProcessMethod.Honey]: "蜜处理",
  [ProcessMethod.Anaerobic]: "厌氧发酵"
};

