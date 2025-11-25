import Form from "@/app/ui/transactions/create-form";
// import Breadcrumbs from "@/app/ui/invoices/breadcrumbs";
// import { fetchCustomers } from "@/app/lib/data";

export default async function Page() {
  // const customers = await fetchCustomers();

  const customers = [
    {
      id: "cust_01ab9c32",
      name: "Ava Thompson",
    },
    {
      id: "cust_02cc7f14",
      name: "Chloe Anderson",
    },
    {
      id: "cust_03df82b9",
      name: "Emily Carter",
    },
    {
      id: "cust_04be61a3",
      name: "Ethan Moore",
    },
    {
      id: "cust_05a9fd81",
      name: "Isabella Flores",
    },
    {
      id: "cust_06c39d55",
      name: "Jordan Lee",
    },
    {
      id: "cust_07e4b1c0",
      name: "Liam Patel",
    },
    {
      id: "cust_08fa22d4",
      name: "Marcus Chen",
    },
    {
      id: "cust_09be74f2",
      name: "Noah Williams",
    },
    {
      id: "cust_10c20aa9",
      name: "Sofia Ramirez",
    },
  ];
  return (
    <main>
      {/* <Breadcrumbs */}
      {/*   breadcrumbs={[ */}
      {/*     { label: "Invoices", href: "/dashboard/invoices" }, */}
      {/*     { */}
      {/*       label: "Create Invoice", */}
      {/*       href: "/dashboard/invoices/create", */}
      {/*       active: true, */}
      {/*     }, */}
      {/*   ]} */}
      {/* /> */}
      <Form customers={customers} />
    </main>
  );
}
