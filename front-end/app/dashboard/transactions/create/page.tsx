import Form from "@/app/ui/transactions/create-form";
// app/dashboard/transactions/create/page.tsx
import { getCurrentUser } from "@/app/lib/auth";
import { redirect } from "next/navigation";

export default async function CreateTransactionPage() {
  const user = await getCurrentUser();

  if (!user) {
    redirect("/login");
  }

  return <Form userId={user.user_id} />;
}
