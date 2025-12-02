import { Card } from "@/app/ui/dashboard/cards";
import RevenueChart from "@/app/ui/dashboard/revenue-chart";
import LatestInvoices from "@/app/ui/dashboard/latest-invoices";
import { getUserStats, getUserItems } from "@/app/lib/data";

function formatCurrency(amount: number) {
  return amount.toLocaleString("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 2,
  });
}

export default async function Page() {
  const userId = 1; // TODO: replace with real logged-in user

  const [stats, items] = await Promise.all([
    getUserStats(userId),
    getUserItems(userId),
  ]);

  return (
    <main>
      <h1 className="mb-4 text-xl md:text-2xl">Dashboard</h1>

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <Card
          title="Revenue"
          value={formatCurrency(stats.totalValue)}
          type="collected"
        />

        {/* REAL ITEMS COUNT HERE */}
        <Card title="Items for Sale" value={items.length} type="pending" />

        <Card
          title="Total Items Sold"
          value={stats.totalTransactions}
          type="invoices"
        />

        <Card
          title="Inventory Value"
          value={formatCurrency(items.length * 39.99)}
          type="customers" // or create a new type icon
        />
      </div>

      <div className="mt-6 grid grid-cols-1 gap-6 md:grid-cols-4 lg:grid-cols-8">
        <RevenueChart />
        <LatestInvoices />
      </div>
    </main>
  );
}
