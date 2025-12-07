import axios from "axios";
import {
  Transaction,
  CreateTransactionPayload,
  UpdateTransactionPayload,
  LoginPayload,
  LoginResponse,
  RegisterPayload,
  RegisterResponse,
  AppUser,
  ItemStat,
  Revenue,
  Organization,
  User,
} from "./definitions";

export const api = axios.create({
  baseURL: "http://localhost:5000", // your backend URL
  withCredentials: true, // 🔑 this is required
});

export async function fetchFirstOrganization(): Promise<Organization | null> {
  const res = await api.get<Organization[] | Organization>("/organizations");
  const data = res.data;

  if (Array.isArray(data)) {
    return data[0] ?? null;
  }
  return data ?? null;
}

// Get organization by id (if you ever want it directly)
export async function fetchOrganizationById(
  organizationId: number,
): Promise<Organization | null> {
  const res = await api.get<Organization>(`/organizations/${organizationId}`);
  return res.data ?? null;
}

// Get all users belonging to an organization
export async function fetchOrganizationUsers(
  organizationId: number,
): Promise<User[]> {
  const res = await api.get<User[]>(`/organizations/${organizationId}/users`);
  return res.data ?? [];
}

// Update organization name
export async function updateOrganizationApi(
  organizationId: number,
  payload: { name: string },
): Promise<Organization> {
  const res = await api.put<Organization>(
    `/organizations/${organizationId}`,
    payload,
  );
  return res.data;
}

// ❗ These assume you’ll have corresponding backend routes:
//   PUT /users/<id> and DELETE /users/<id>

export async function deleteUserApi(userId: number): Promise<void> {
  await api.delete(`/users/${userId}`);
}

export async function updateUserApi(
  userId: number,
  payload: Partial<User>,
): Promise<User> {
  const res = await api.put<User>(`/users/${userId}`, payload);
  return res.data;
}

export async function fetchLatestTransactions(userId: number) {
  const res = await api.get<Transaction[]>(`/users/${userId}/transactions`);
  const rows = res.data ?? [];

  // Sort newest → oldest
  rows.sort(
    (a, b) => new Date(b.sale_date).getTime() - new Date(a.sale_date).getTime(),
  );

  // Return last 5
  return rows.slice(0, 5);
}

// Auth
export async function login(payload: LoginPayload): Promise<LoginResponse> {
  try {
    const res = await api.post<LoginResponse>("/login", payload, {
      withCredentials: true, // ensure auth_token cookie is set if cross-origin
    });
    return res.data;
  } catch (err: any) {
    const backendError = err?.response?.data?.error;
    if (backendError) {
      // e.g., "Invalid username or password"
      throw new Error(backendError);
    }
    throw err;
  }
}

export async function registerUser(
  payload: RegisterPayload,
): Promise<RegisterResponse> {
  const res = await api.post<RegisterResponse>("/register", payload);
  return res.data;
}

export async function getUserById(userId: number): Promise<AppUser> {
  const res = await api.get<AppUser>(`/users/${userId}`);
  return res.data;
}

export async function getTransactions(): Promise<Transaction[]> {
  const response = await api.get<Transaction[]>("/users/1/transactions");
  return response.data;
}

export async function createTransaction(
  payload: CreateTransactionPayload,
): Promise<Transaction> {
  const response = await api.post<Transaction>("/transactions", payload);
  return response.data;
}

export async function createUser(
  payload: RegisterPayload,
): Promise<RegisterResponse> {
  try {
    const res = await api.post<RegisterResponse>("/register", payload);
    return res.data;
  } catch (err: any) {
    if (err?.response?.data) {
      return err.response.data as RegisterResponse;
    }
    throw err;
  }
}

export async function getUserItems(userId: number): Promise<ItemStat[]> {
  const res = await api.get<ItemStat[]>(`/users/${userId}/items`);
  return res.data;
}

export async function updateTransaction(
  transactionId: number,
  payload: UpdateTransactionPayload,
): Promise<Transaction> {
  const response = await api.patch<Transaction>(
    `/transactions/${transactionId}`,
    payload,
  );
  return response.data;
}

export async function deleteTransaction(transactionId: number) {
  const response = await api.delete(`/transactions/${transactionId}`);
  return response.data;
}

// Transaction Stats for Account Page
export async function getUserTransactions(
  userId: number,
): Promise<Transaction[]> {
  // you already effectively have this as /users/<id>/transactions
  const res = await api.get<Transaction[]>(`/users/${userId}/transactions`);
  return res.data;
}

export type UserStats = {
  totalTransactions: number;
  totalValue: number;
  lastActivity: string | null; // ISO date string or null if none
};

export async function getUserStats(userId: number): Promise<UserStats> {
  const txns = await getUserTransactions(userId);

  if (txns.length === 0) {
    return {
      totalTransactions: 0,
      totalValue: 0,
      lastActivity: null,
    };
  }

  const totalTransactions = txns.length;
  const totalValue = txns.reduce((sum, t) => sum + (t.total ?? 0), 0);

  // Find latest sale_date
  const lastActivityDate = txns
    .map((t) => t.sale_date)
    .filter(Boolean)
    .sort()
    .at(-1)!; // last (max) date string

  return {
    totalTransactions,
    totalValue,
    lastActivity: lastActivityDate,
  };
}

// Revenue Chart Functions
function getLast12Months(): { key: string; label: string }[] {
  const result: { key: string; label: string }[] = [];
  const now = new Date();

  for (let i = 11; i >= 0; i--) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
    const year = d.getFullYear();
    const month = d.getMonth(); // 0-11
    const key = `${year}-${String(month + 1).padStart(2, "0")}`; // e.g. "2025-03"
    const label = d.toLocaleString("en-US", { month: "short" }); // "Jan"
    result.push({ key, label });
  }

  return result;
}

export async function fetchRevenue(userId: number): Promise<Revenue[]> {
  const res = await api.get<Transaction[]>(`/users/${userId}/transactions`);
  const transactions = res.data ?? [];

  const months = getLast12Months();
  const bucket: Record<string, number> = {};
  for (const m of months) {
    bucket[m.key] = 0;
  }

  for (const tx of transactions) {
    if (!tx.sale_date || tx.total == null) continue;

    const d = new Date(tx.sale_date);
    if (Number.isNaN(d.getTime())) continue;

    const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(
      2,
      "0",
    )}`;

    if (key in bucket) {
      bucket[key] += tx.total;
    }
  }

  const revenue: Revenue[] = months.map((m) => ({
    month: m.label,
    revenue: bucket[m.key] ?? 0,
  }));

  return revenue;
}

export async function logout(): Promise<void> {
  try {
    await api.post(
      "/logout",
      {},
      {
        withCredentials: true, // ensures auth_token cookie is sent
      },
    );
  } catch (err) {
    console.error("Logout failed:", err);
    throw err;
  }
}
