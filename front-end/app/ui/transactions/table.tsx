// app/dashboard/transactions/InvoicesTable.tsx
import { PencilIcon, TrashIcon } from "@heroicons/react/24/outline";
import Link from "next/link";
import { getUserTransactions } from "@/app/lib/data"; // ⬅️ use user-specific fn
import { type Transaction } from "@/app/lib/definitions";
import { DeleteInvoice } from "@/app/ui/transactions/buttons";
import { getCurrentUser } from "@/app/lib/auth"; // ⬅️ read JWT cookie
import { redirect } from "next/navigation";

export function UpdateInvoice({ id }: { id: string }) {
  return (
    <Link
      href={`/dashboard/transactions/edit?id=${id}`}
      className="rounded-md border p-2 hover:bg-gray-100"
    >
      <PencilIcon className="w-5" />
    </Link>
  );
}

export default async function InvoicesTable({
  query,
  currentPage,
}: {
  query: string;
  currentPage: number;
}) {
  // 🔐 get logged-in user from auth_token cookie
  const user = await getCurrentUser();
  if (!user) {
    redirect("/login");
  }

  const userId = user.user_id;

  // 🔢 only fetch THIS user's transactions
  const transactions: Transaction[] = await getUserTransactions(userId);

  return (
    <div className="mt-6 flow-root">
      <div className="inline-block min-w-full align-middle">
        <div className="rounded-lg bg-gray-50 p-2 md:pt-0">
          {/* Mobile cards */}
          <div className="md:hidden">
            {transactions.map((transaction) => (
              <div
                key={transaction.transaction_id}
                className="mb-2 w-full rounded-md bg-white p-4"
              >
                <div className="flex items-center justify-between border-b pb-4">
                  <p className="text-sm text-gray-500">
                    Transaction #{transaction.transaction_id}
                  </p>
                </div>

                <div className="flex w-full items-center justify-between pt-4">
                  <div>
                    <p className="text-xl font-medium">
                      ${transaction.total.toFixed(2)}
                    </p>
                    <p className="text-sm text-gray-500">
                      Date: {transaction.sale_date}
                    </p>
                    <p className="text-xs text-gray-500">
                      Tax: ${transaction.tax.toFixed(2)} · Comm: $
                      {transaction.seller_comission.toFixed(2)}
                    </p>
                  </div>
                  <div className="flex justify-end gap-2">
                    <UpdateInvoice id={String(transaction.transaction_id)} />
                    <DeleteInvoice id={String(transaction.transaction_id)} />
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Desktop table */}
          <table className="hidden min-w-full text-gray-900 md:table">
            <thead className="rounded-lg text-left text-sm font-normal">
              <tr>
                <th scope="col" className="px-4 py-5 font-medium sm:pl-6">
                  ID
                </th>
                <th scope="col" className="px-3 py-5 font-medium">
                  Total
                </th>
                <th scope="col" className="px-3 py-5 font-medium">
                  Tax
                </th>
                <th scope="col" className="px-3 py-5 font-medium">
                  Commission
                </th>
                <th scope="col" className="px-3 py-5 font-medium">
                  Date
                </th>
                <th scope="col" className="relative py-3 pl-6 pr-3">
                  <span className="sr-only">Actions</span>
                </th>
              </tr>
            </thead>
            <tbody className="bg-white">
              {transactions.map((transaction) => (
                <tr
                  key={transaction.transaction_id}
                  className="w-full border-b py-3 text-sm last-of-type:border-none
                    [&:first-child>td:first-child]:rounded-tl-lg
                    [&:first-child>td:last-child]:rounded-tr-lg
                    [&:last-child>td:first-child]:rounded-bl-lg
                    [&:last-child>td:last-child]:rounded-br-lg"
                >
                  <td className="whitespace-nowrap py-3 pl-6 pr-3">
                    #{transaction.transaction_id}
                  </td>
                  <td className="whitespace-nowrap px-3 py-3">
                    ${transaction.total.toFixed(2)}
                  </td>
                  <td className="whitespace-nowrap px-3 py-3">
                    ${transaction.tax.toFixed(2)}
                  </td>
                  <td className="whitespace-nowrap px-3 py-3">
                    ${transaction.seller_comission.toFixed(2)}
                  </td>
                  <td className="whitespace-nowrap px-3 py-3">
                    {transaction.sale_date}
                  </td>
                  <td className="whitespace-nowrap py-3 pl-6 pr-3">
                    <div className="flex justify-end gap-3">
                      <UpdateInvoice id={String(transaction.transaction_id)} />
                      <DeleteInvoice id={String(transaction.transaction_id)} />
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {transactions.length === 0 && (
            <p className="p-4 text-sm text-gray-500">No transactions found.</p>
          )}
        </div>
      </div>
    </div>
  );
}
