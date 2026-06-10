import type { ProcessMethod } from "./enums";

export interface CoffeeBean {
  id: number;
  name: string;
  origin: string;
  process_method: ProcessMethod;
  flavor_tags: string[];
  description: string;
}

export interface BeanPayload {
  name: string;
  origin: string;
  process_method: ProcessMethod;
  flavor_tags: string[];
  description: string;
}

