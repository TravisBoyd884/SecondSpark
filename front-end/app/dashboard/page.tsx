// app/dashboard/page.tsx (or wherever this page lives)
import { Card } from "@/app/ui/dashboard/cards";
import RevenueChart from "@/app/ui/dashboard/revenue-chart";
import LatestInvoices from "@/app/ui/dashboard/latest-invoices";
import { getUserStats, getUserItems } from "@/app/lib/data";
import { getCurrentUser } from "@/app/lib/auth";
import { redirect } from "next/navigation";

function formatCurrency(amount: number) {
  return amount.toLocaleString("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 2,
  });
}

export default async function Page() {
  const user = await getCurrentUser();

  // If not logged in, send them to login
  if (!user) {
    redirect("/login");
  }

  const userId = user.user_id;

  const [stats, items] = await Promise.all([
    getUserStats(userId),
    getUserItems(userId),
  ]);

  return (
    <main>
      <h1 className="mb-4 text-xl md:text-2xl">
        Dashboard – Welcome, {user.username}
      </h1>

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <Card
          title="Revenue"
          value={formatCurrency(stats.totalValue)}
          type="collected"
        />

        <Card title="Items for Sale" value={items.length} type="pending" />

        <Card
          title="Total Items Sold"
          value={stats.totalTransactions}
          type="invoices"
        />

        <Card
          title="Inventory Value"
          value={formatCurrency(items.length * 39.99)}
          type="customers"
        />
      </div>

      <div className="mt-6 grid grid-cols-1 gap-6 md:grid-cols-4 lg:grid-cols-8">
        <RevenueChart />
        <LatestInvoices />
      </div>
    </main>
  );
}
