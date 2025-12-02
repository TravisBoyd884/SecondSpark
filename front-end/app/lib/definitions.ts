// This file contains type definitions for your data.
// It describes the shape of the data, and what data type each property should accept.
// For simplicity of teaching, we're manually defining these types.
// However, these types are generated automatically if you're using an ORM such as Prisma.
export interface Organization {
  organization_id: number;
  name: string;
}

export interface User {
  user_id: number;
  username: string;
  email: string;

  // Foreign keys / relationships
  organization_id: number | null;
  organization_role: string | null;

  // Marketplace accounts (can be null if not linked)
  ebay_account_id?: number | null;
  etsy_account_id?: number | null;

  // Frontend-only / form-only field (not returned by backend)
  password?: string;
}

export type Item = {
  item_id: string;
  title: string;
  description: string;
  category: string;
  list_date: string;
  price: number;
  isOnEtsy: boolean;
  isOnEbay: boolean;
  creator_id: string;
};

export type Reseller = {
  reseller_id: string;
  reseller_name: string;
};

export type Transaction = {
  transaction_id: number;
  sale_date: string;
  total: number;
  tax: number;
  seller_comission: number;
};

export type CreateTransactionPayload = {
  sale_date: string;
  total: number;
  tax?: number;
  reseller_comission?: number;
  reseller_id: number;
  status?: string; // optional – backend can ignore if not used
};

export type UpdateTransactionPayload = Partial<{
  sale_date: string;
  total: number;
  tax: number;
  reseller_comission: number;
  reseller_id: number;
}>;

export type ItemStat = {
  item_id: number;
  name: string;
};

export type AppUser = {
  user_id: number;
  username: string;
  email: string;
  organization_id: number | null;
  organization_role: string | null;
};

export type LoginPayload = {
  username: string;
  password: string;
};

export type LoginResponse = {
  message: string;
  user: AppUser;
};

export type RegisterPayload = {
  username: string;
  password: string;
  email: string;
  organization_id: number;
};

export type RegisterResponse = {
  message: string;
  user_id: number;
};

export type Transaction_Item = {
  transaction_item_id: string;
  item_id: string;
  transaction_id: string;
};

export type Customer = {
  id: string;
  name: string;
  email: string;
  image_url: string;
};

export type Invoice = {
  id: string;
  customer_id: string;
  amount: number;
  date: string;
  // In TypeScript, this is called a string union type.
  // It means that the "status" property can only be one of the two strings: 'pending' or 'paid'.
  status: "pending" | "paid";
};

export type Revenue = {
  month: string;
  revenue: number;
};

export type LatestInvoice = {
  id: string;
  name: string;
  image_url: string;
  email: string;
  amount: string;
};

// The database returns a number for amount, but we later format it to a string with the formatCurrency function
export type LatestInvoiceRaw = Omit<LatestInvoice, "amount"> & {
  amount: number;
};

export type InvoicesTable = {
  id: string;
  customer_id: string;
  name: string;
  email: string;
  image_url: string;
  date: string;
  amount: number;
  status: "pending" | "paid";
};

export type CustomersTableType = {
  id: string;
  name: string;
  email: string;
  image_url: string;
  total_invoices: number;
  total_pending: number;
  total_paid: number;
};

export type FormattedCustomersTable = {
  id: string;
  name: string;
  email: string;
  image_url: string;
  total_invoices: number;
  total_pending: string;
  total_paid: string;
};

export type CustomerField = {
  id: string;
  name: string;
};

export type InvoiceForm = {
  id: string;
  customer_id: string;
  amount: number;
  status: "pending" | "paid";
};
