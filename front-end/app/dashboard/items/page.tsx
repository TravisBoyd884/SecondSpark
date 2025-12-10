// app/dashboard/items/page.tsx
import { getCurrentUser } from "@/app/lib/auth";
import { redirect } from "next/navigation";
import { getUserById } from "@/app/lib/data";
import ItemsGridTest from "./itemsGridTest";

export default async function Page() {
  const currentUser = await getCurrentUser();

  // Not logged in → kick to login
  if (!currentUser) {
    redirect("/login");
  }

  const userId = currentUser.user_id;

  // Fetch full user data to get organization_role
  const user = await getUserById(userId);
  const isAdmin = user.organization_role === "Admin";

  return (
    <div>
      <h1 className="text-2xl font-bold text-center">Inventory</h1>
      <ItemsGridTest userId={user.user_id} isAdmin={isAdmin} />
    </div>
  );
}
