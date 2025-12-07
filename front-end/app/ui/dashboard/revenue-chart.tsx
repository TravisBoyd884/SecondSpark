// app/ui/dashboard/revenue-chart.tsx
import { CalendarIcon } from "@heroicons/react/24/outline";
import { fetchRevenue } from "@/app/lib/data";
import { getCurrentUser } from "@/app/lib/auth";
import { redirect } from "next/navigation";

function formatCurrency(amount: number) {
  return amount.toLocaleString("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  });
}

export default async function RevenueChart() {
  // 🔐 Get logged-in user from auth_token cookie
  const user = await getCurrentUser();
  if (!user) {
    redirect("/login");
  }

  const userId = user.user_id;

  // 💰 Fetch revenue for THIS user
  const revenue = await fetchRevenue(userId);
  const chartHeight = 350;

  if (!revenue || revenue.length === 0) {
    return (
      <div className="w-full md:col-span-4">
        <h2 className="mb-4 text-xl md:text-2xl">Recent Revenue</h2>
        <div className="rounded-xl bg-gray-50 p-4">
          <div className="rounded-md bg-white p-6 text-sm text-gray-400">
            No revenue data available.
          </div>
        </div>
      </div>
    );
  }

  const maxRevenue = Math.max(...revenue.map((r) => r.revenue), 0);
  const safeMax = maxRevenue || 100;
  const step = safeMax / 5;

  const yAxisLabels = Array.from({ length: 6 }, (_, i) =>
    formatCurrency(step * (5 - i)),
  );

  return (
    <div className="w-full md:col-span-4">
      <h2 className="mb-4 text-xl md:text-2xl">Recent Revenue</h2>

      <div className="rounded-xl bg-gray-50 p-4">
        <div className="sm:grid-cols-13 mt-0 grid grid-cols-12 items-end gap-2 rounded-md bg-white p-4 md:gap-4">
          {/* Y-axis labels */}
          <div
            className="mb-6 hidden flex-col justify-between text-sm text-gray-400 sm:flex"
            style={{ height: `${chartHeight}px` }}
          >
            {yAxisLabels.map((label) => (
              <p key={label}>{label}</p>
            ))}
          </div>

          {/* Bars */}
          {revenue.map((month) => (
            <div key={month.month} className="flex flex-col items-center gap-2">
              <div
                className="w-full rounded-md bg-blue-300"
                style={{
                  height: `${(chartHeight * month.revenue) / safeMax}px`,
                }}
              ></div>
              <p className="-rotate-90 text-sm text-gray-400 sm:rotate-0">
                {month.month}
              </p>
            </div>
          ))}
        </div>
        <div className="flex items-center pb-2 pt-6">
          <CalendarIcon className="h-5 w-5 text-gray-500" />
          <h3 className="ml-2 text-sm text-gray-500">Last 12 months</h3>
        </div>
      </div>
    </div>
  );
}
