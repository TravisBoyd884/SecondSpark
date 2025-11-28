import Image from "next/image";
// import { UpdateInvoice, DeleteInvoice } from "@/app/ui/transactions/buttons";
// import InvoiceStatus from "@/app/ui/transactions/status";
// import { formatDateToLocal, formatCurrency } from "@/app/lib/utils";
// import { fetchFilteredInvoices } from "@/app/lib/data";
import { PencilIcon, TrashIcon } from "@heroicons/react/24/outline";
import Link from "next/link";
import { getTransactions } from "@/app/lib/data";

export function UpdateInvoice({ id }: { id: string }) {
  return (
    <Link
      href={`/dashboard/transactions/edit`}
      className="rounded-md border p-2 hover:bg-gray-100"
    >
      <PencilIcon className="w-5" />
    </Link>
  );
}

export function DeleteInvoice({ id }: { id: string }) {
  // const deleteInvoiceWithId = deleteInvoice.bind(null, id);
  return (
    <form action={""}>
      <button type="submit" className="rounded-md border p-2 hover:bg-gray-100">
        <span className="sr-only">Delete</span>
        <TrashIcon className="w-5" />
      </button>
    </form>
  );
}

export default async function InvoicesTable({
  query,
  currentPage,
}: {
  query: string;
  currentPage: number;
}) {
  const transactions = await getTransactions();
  return (
    <div className="mt-6 flow-root">
      <div className="inline-block min-w-full align-middle">
        <div className="rounded-lg bg-gray-50 p-2 md:pt-0">
          <div className="md:hidden">
            {transactions?.map((transaction) => (
              <div
                key={transaction.transaction_id}
                className="mb-2 w-full rounded-md bg-white p-4"
              >
                <div className="flex items-center justify-between border-b pb-4">
                  <div>
                    {/* <div className="mb-2 flex items-center"> */}
                    {/*   <p>{transaction.name}</p> */}
                    {/* </div> */}
                  </div>
                </div>
                <div className="flex w-full items-center justify-between pt-4">
                  <div>
                    <p className="text-xl font-medium">
                      {/* {formatCurrency(transaction.amount)} */}
                      {transaction.total}
                    </p>
                    {/* <p>{formatDateToLocal(transaction.date)}</p> */}
                    <p>{transaction.sale_date}</p>
                  </div>
                  <div className="flex justify-end gap-2">
                    <UpdateInvoice id={transaction.transaction_id} />
                    <DeleteInvoice id={transaction.transaction_id} />
                  </div>
                </div>
              </div>
            ))}
          </div>
          <table className="hidden min-w-full text-gray-900 md:table">
            <thead className="rounded-lg text-left text-sm font-normal">
              <tr>
                <th scope="col" className="px-4 py-5 font-medium sm:pl-6">
                  Customer
                </th>
                <th scope="col" className="px-3 py-5 font-medium">
                  Email
                </th>
                <th scope="col" className="px-3 py-5 font-medium">
                  Amount
                </th>
                <th scope="col" className="px-3 py-5 font-medium">
                  Date
                </th>
                <th scope="col" className="px-3 py-5 font-medium">
                  Status
                </th>
                <th scope="col" className="relative py-3 pl-6 pr-3">
                  <span className="sr-only">Edit</span>
                </th>
              </tr>
            </thead>
            <tbody className="bg-white">
              {transactions?.map((transaction) => (
                <tr
                  key={transaction.transaction_id}
                  className="w-full border-b py-3 text-sm last-of-type:border-none [&:first-child>td:first-child]:rounded-tl-lg [&:first-child>td:last-child]:rounded-tr-lg [&:last-child>td:first-child]:rounded-bl-lg [&:last-child>td:last-child]:rounded-br-lg"
                >
                  <td className="whitespace-nowrap py-3 pl-6 pr-3">
                    {/* <div className="flex items-center gap-3"> */}
                    {/*   <p>{transaction.}</p> */}
                    {/* </div> */}
                  </td>
                  {/* <td className="whitespace-nowrap px-3 py-3"> */}
                  {/*   {transaction.email} */}
                  {/* </td> */}
                  <td className="whitespace-nowrap px-3 py-3">
                    {transaction.sale_date}
                  </td>
                  <td className="whitespace-nowrap px-3 py-3">
                    {transaction.sale_date}
                  </td>
                  {/* <td className="whitespace-nowrap px-3 py-3"> */}
                  {/*   {transaction.status} */}
                  {/* </td> */}
                  <td className="whitespace-nowrap py-3 pl-6 pr-3">
                    <div className="flex justify-end gap-3">
                      <UpdateInvoice id={transaction.transaction_id} />
                      <DeleteInvoice id={transaction.transaction_id} />
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
