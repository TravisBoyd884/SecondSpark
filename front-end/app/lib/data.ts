import axios from "axios";
import { Transaction } from "./definitions";

export const api = axios.create({
  baseURL: "http://127.0.0.1:5000", // Flask default
});

export async function getTransactions(): Promise<Transaction[]> {
  const response = await api.get<Transaction[]>("/transactions");
  return response.data;
}
