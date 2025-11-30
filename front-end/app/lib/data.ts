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
  organization_id,
}: {
  username: string;
  password: string;
  email: string;
  organization_id: number;
}) {
  try {
    const res = await api.post("/register", {
      username,
      password,
      email,
      organization_id,
    });

    // backend returns: { message: string, user_id: number }
    return res.data;
  } catch (err: any) {
    if (err.response) return err.response.data;
    throw err;
  }
}
