import Image from "next/image";
// import { UpdateInvoice, DeleteInvoice } from "@/app/ui/invoices/buttons";
// import InvoiceStatus from "@/app/ui/invoices/status";
// import { formatDateToLocal, formatCurrency } from "@/app/lib/utils";
// import { fetchFilteredInvoices } from "@/app/lib/data";
import { PencilIcon, TrashIcon } from "@heroicons/react/24/outline";
import Link from "next/link";

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
  const invoices = [
    {
      id: "inv_01f9a7c2",
      amount: 243.18,
      date: "2024-11-12",
      status: "paid",
      name: "Jordan Lee",
      email: "jordan.lee@gmail.com",
      image_url: "https://randomuser.me/api/portraits/men/12.jpg",
    },
    {
      id: "inv_02c7bd55",
      amount: 129.5,
      date: "2024-10-29",
      status: "pending",
      name: "Sofia Ramirez",
      email: "sofia.ramirez@yahoo.com",
      image_url: "https://randomuser.me/api/portraits/women/22.jpg",
    },
    {
      id: "inv_03a98fd2",
      amount: 382.77,
      date: "2024-10-15",
      status: "overdue",
      name: "Marcus Chen",
      email: "marcus.chen@outlook.com",
      image_url: "https://randomuser.me/api/portraits/men/45.jpg",
    },
    {
      id: "inv_04e2c1aa",
      amount: 199.99,
      date: "2024-09-30",
      status: "paid",
      name: "Ava Thompson",
      email: "ava.thompson@icloud.com",
      image_url: "https://randomuser.me/api/portraits/women/31.jpg",
    },
    {
      id: "inv_05fb83d9",
      amount: 87.4,
      date: "2024-09-12",
      status: "pending",
      name: "Liam Patel",
      email: "liam.patel@hotmail.com",
      image_url: "https://randomuser.me/api/portraits/men/67.jpg",
    },
    {
      id: "inv_06e99a31",
      amount: 422.11,
      date: "2024-08-25",
      status: "paid",
      name: "Emily Carter",
      email: "emily.carter@aol.com",
      image_url: "https://randomuser.me/api/portraits/women/55.jpg",
    },
    {
      id: "inv_07b2ef71",
      amount: 156.75,
      date: "2024-08-10",
      status: "overdue",
      name: "Noah Williams",
      email: "noah.williams@gmail.com",
      image_url: "https://randomuser.me/api/portraits/men/75.jpg",
    },
    {
      id: "inv_08c72dd4",
      amount: 311.45,
      date: "2024-07-28",
      status: "pending",
      name: "Isabella Flores",
      email: "isabella.flores@yahoo.com",
      image_url: "https://randomuser.me/api/portraits/women/49.jpg",
    },
    {
      id: "inv_09adf6c3",
      amount: 98.23,
      date: "2024-07-05",
      status: "paid",
      name: "Ethan Moore",
      email: "ethan.moore@gmail.com",
      image_url: "https://randomuser.me/api/portraits/men/28.jpg",
    },
    {
      id: "inv_10e8c7bb",
      amount: 455.1,
      date: "2024-06-19",
      status: "overdue",
      name: "Chloe Anderson",
      email: "chloe.anderson@icloud.com",
      image_url: "https://randomuser.me/api/portraits/women/16.jpg",
    },
  ];
  return (
    <div className="mt-6 flow-root">
      <div className="inline-block min-w-full align-middle">
        <div className="rounded-lg bg-gray-50 p-2 md:pt-0">
          <div className="md:hidden">
            {invoices?.map((invoice) => (
              <div
                key={invoice.id}
                className="mb-2 w-full rounded-md bg-white p-4"
              >
                <div className="flex items-center justify-between border-b pb-4">
                  <div>
                    <div className="mb-2 flex items-center">
                      {/* <Image */}
                      {/*   src={invoice.image_url} */}
                      {/*   className="mr-2 rounded-full" */}
                      {/*   width={28} */}
                      {/*   height={28} */}
                      {/*   alt={`${invoice.name}'s profile picture`} */}
                      {/* /> */}
                      <p>{invoice.name}</p>
                    </div>
                    <p className="text-sm text-gray-500">{invoice.email}</p>
                  </div>
                  {/* <InvoiceStatus status={invoice.status} /> */}
                </div>
                <div className="flex w-full items-center justify-between pt-4">
                  <div>
                    <p className="text-xl font-medium">
                      {/* {formatCurrency(invoice.amount)} */}
                      {invoice.amount}
                    </p>
                    {/* <p>{formatDateToLocal(invoice.date)}</p> */}
                    <p>{invoice.amount}</p>
                  </div>
                  <div className="flex justify-end gap-2">
                    <UpdateInvoice id={invoice.id} />
                    <DeleteInvoice id={invoice.id} />
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
              {invoices?.map((invoice) => (
                <tr
                  key={invoice.id}
                  className="w-full border-b py-3 text-sm last-of-type:border-none [&:first-child>td:first-child]:rounded-tl-lg [&:first-child>td:last-child]:rounded-tr-lg [&:last-child>td:first-child]:rounded-bl-lg [&:last-child>td:last-child]:rounded-br-lg"
                >
                  <td className="whitespace-nowrap py-3 pl-6 pr-3">
                    <div className="flex items-center gap-3">
                      {/* <Image */}
                      {/*   src={invoice.image_url} */}
                      {/*   className="rounded-full" */}
                      {/*   width={28} */}
                      {/*   height={28} */}
                      {/*   alt={`${invoice.name}'s profile picture`} */}
                      {/* /> */}
                      <p>{invoice.name}</p>
                    </div>
                  </td>
                  <td className="whitespace-nowrap px-3 py-3">
                    {invoice.email}
                  </td>
                  {/* <td className="whitespace-nowrap px-3 py-3"> */}
                  {/*   {formatCurrency(invoice.amount)} */}
                  {/* </td> */}
                  <td className="whitespace-nowrap px-3 py-3">
                    {invoice.date}
                  </td>
                  {/* <td className="whitespace-nowrap px-3 py-3"> */}
                  {/*   {formatDateToLocal(invoice.date)} */}
                  {/* </td> */}
                  <td className="whitespace-nowrap px-3 py-3">
                    {invoice.date}
                  </td>
                  <td className="whitespace-nowrap px-3 py-3">
                    {/* <InvoiceStatus status={invoice.status} /> */}
                    {invoice.status}
                  </td>
                  <td className="whitespace-nowrap py-3 pl-6 pr-3">
                    <div className="flex justify-end gap-3">
                      <UpdateInvoice id={invoice.id} />
                      <DeleteInvoice id={invoice.id} />
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
