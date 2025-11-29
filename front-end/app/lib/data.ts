import axios from "axios";
import { Transaction } from "./definitions";

export const api = axios.create({
  baseURL: "http://127.0.0.1:5000", // Flask default
});

export async function getTransactions(): Promise<Transaction[]> {
  const response = await api.get<Transaction[]>("/transactions");
  return response.data;
}

export async function login(username: string, password: string) {
  try {
    const res = await api.post("/login", {
      username,
      password,
    });

    return res.data; // contains { message, user }
  } catch (err: any) {
    if (err.response) {
      return err.response.data; // backend error message
    }
    throw err;
  }
}

export async function createUser({
  username,
  password,
  email,
  organization_id = null,
  organization_role = null,
  ebay_account_id = null,
  etsy_account_id = null,
}: {
  username: string;
  password: string;
  email: string;
  organization_id?: number | null;
  organization_role?: string | null;
  ebay_account_id?: number | null;
  etsy_account_id?: number | null;
}) {
  try {
    const res = await api.post("/create_app_user", {
      username,
      password,
      email,
      organization_id,
      organization_role,
      ebay_account_id,
      etsy_account_id,
    });

    return res.data; // "User created successfully"
  } catch (err: any) {
    if (err.response) return err.response.data;
    throw err;
  }
}
