import { ArrowPathIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";
import { fetchLatestTransactions } from "@/app/lib/data";

function formatCurrency(amount: number) {
  return amount.toLocaleString("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 2,
  });
}

function formatDate(dateStr: string) {
  const d = new Date(dateStr);
  return d.toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export default async function LatestTransactions() {
  const userId = 1; // TODO: replace with real logged-in user
  const transactions = await fetchLatestTransactions(userId);

  return (
    <div className="flex w-full flex-col md:col-span-4">
      <h2 className="mb-4 text-xl md:text-2xl">Latest Transactions</h2>

      <div className="flex grow flex-col justify-between rounded-xl bg-gray-50 p-4">
        <div className="bg-white px-6">
          {transactions.length === 0 && (
            <p className="py-4 text-sm text-gray-500">No transactions yet.</p>
          )}

          {transactions.map((t, i) => (
            <div
              key={t.transaction_id}
              className={clsx(
                "flex flex-row items-center justify-between py-4",
                { "border-t": i !== 0 },
              )}
            >
              <div className="min-w-0">
                <p className="text-sm font-semibold md:text-base">
                  {formatCurrency(t.total)}
                </p>
                <p className="text-sm text-gray-500">
                  {formatDate(t.sale_date)}
                </p>
              </div>

              <p className="truncate text-sm text-gray-400">
                #{t.transaction_id}
              </p>
            </div>
          ))}
        </div>

        <div className="flex items-center pb-2 pt-6">
          <ArrowPathIcon className="h-5 w-5 text-gray-500" />
          <h3 className="ml-2 text-sm text-gray-500">Updated just now</h3>
        </div>
      </div>
    </div>
  );
}
