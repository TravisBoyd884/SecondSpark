import { ArrowPathIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";
import Image from "next/image";
// import { lusitana } from "@/app/ui/fonts";
import { LatestInvoice } from "@/app/lib/definitions";
// import { fetchLatestInvoices } from "@/app/lib/data";

export default async function LatestInvoices() {
  // const latestInvoices = await fetchLatestInvoices();
  const latestInvoices = [
    {
      id: "a1f3c8e2-4bd1-4c9e-af19-842c1e9e12aa",
      name: "Jordan Lee",
      image_url: "https://randomuser.me/api/portraits/men/12.jpg",
      email: "jordan.lee@example.com",
      amount: "$243.18",
    },
    {
      id: "b9d47ac1-28e0-4c6c-9f32-7b94ee3185cd",
      name: "Sofia Ramirez",
      image_url: "https://randomuser.me/api/portraits/women/22.jpg",
      email: "sofia.ramirez@example.com",
      amount: "$129.50",
    },
    {
      id: "c87af34d-1f9a-45d5-a41b-42c9e5fa9c31",
      name: "Marcus Chen",
      image_url: "https://randomuser.me/api/portraits/men/45.jpg",
      email: "marcus.chen@example.com",
      amount: "$382.77",
    },
    {
      id: "df3b2984-51b3-40a0-8c54-5f88c1c25fb7",
      name: "Ava Thompson",
      image_url: "https://randomuser.me/api/portraits/women/31.jpg",
      email: "ava.thompson@example.com",
      amount: "$199.99",
    },
    {
      id: "e4c92bc0-52ab-4964-a3bf-2ea65cb3d92f",
      name: "Liam Patel",
      image_url: "https://randomuser.me/api/portraits/men/67.jpg",
      email: "liam.patel@example.com",
      amount: "$87.40",
    },
    {
      id: "fa1290e4-8cf1-47f4-90a3-6c29147e9be2",
      name: "Emily Carter",
      image_url: "https://randomuser.me/api/portraits/women/55.jpg",
      email: "emily.carter@example.com",
      amount: "$422.11",
    },
  ];

  return (
    <div className="flex w-full flex-col md:col-span-4">
      <h2 className={` mb-4 text-xl md:text-2xl`}>Latest Sales</h2>
      <div className="flex grow flex-col justify-between rounded-xl bg-gray-50 p-4">
        {/* NOTE: Uncomment this code in Chapter 7 */}

        <div className="bg-white px-6">
          {latestInvoices.map((invoice, i) => {
            return (
              <div
                key={invoice.id}
                className={clsx(
                  "flex flex-row items-center justify-between py-4",
                  {
                    "border-t": i !== 0,
                  },
                )}
              >
                <div className="flex items-center">
                  {/* <Image */}
                  {/*   src={invoice.image_url} */}
                  {/*   alt={`${invoice.name}'s profile picture`} */}
                  {/*   className="mr-4 rounded-full" */}
                  {/*   width={32} */}
                  {/*   height={32} */}
                  {/* /> */}
                  <div className="min-w-0">
                    <p className="truncate text-sm font-semibold md:text-base">
                      {invoice.name}
                    </p>
                    <p className="hidden text-sm text-gray-500 sm:block">
                      {invoice.email}
                    </p>
                  </div>
                </div>
                <p className={` truncate text-sm font-medium md:text-base`}>
                  {invoice.amount}
                </p>
              </div>
            );
          })}
        </div>
        <div className="flex items-center pb-2 pt-6">
          <ArrowPathIcon className="h-5 w-5 text-gray-500" />
          <h3 className="ml-2 text-sm text-gray-500 ">Updated just now</h3>
        </div>
      </div>
    </div>
  );
}
