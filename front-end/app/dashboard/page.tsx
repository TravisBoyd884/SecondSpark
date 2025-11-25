import { Card } from "@/app/ui/dashboard/cards";
import Image from "next/image";
import RevenueChart from "@/app/ui/dashboard/revenue-chart";
import LatestInvoices from "@/app/ui/dashboard/latest-invoices";

export default async function Page() {
  return (
    <main>
      <h1 className={`mb-4 text-xl md:text-2xl`}>Dashboard</h1>
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <Card title="Revenue" value={"$3,609.74"} type="collected" />
        <Card title="Items for Sale" value={48} type="pending" />
        <Card title="Total Items Sold" value={33} type="invoices" />
        <Card title="Total Customers" value={21} type="customers" />
      </div>
      <div className="mt-6 grid grid-cols-1 gap-6 md:grid-cols-4 lg:grid-cols-8">
        <RevenueChart />
        {/* <div> */}
        <LatestInvoices />
      </div>
    </main>
  );
}
