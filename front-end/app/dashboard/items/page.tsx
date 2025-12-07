// app/dashboard/items/page.tsx
import { getCurrentUser } from "@/app/lib/auth";
import { redirect } from "next/navigation";
import ItemsGridTest from "./itemsGridTest";

export default async function Page() {
  const user = await getCurrentUser();

  if (!user) {
    redirect("/login");
  }
  return (
    <div>
      <h1 className="text-2xl font-bold text-center">Inventory</h1>
      <ItemsGridTest userId={user.user_id} />;
    </div>
  );
}
