import Pagination from "@/app/ui/transactions/pagination";
import Search from "@/app/ui/search";
import Table from "@/app/ui/transactions/table";
// import { CreateInvoice } from "@/app/ui/transactions/buttons";
// import { InvoicesTableSkeleton } from "@/app/ui/skeletons";
import { Suspense } from "react";
import Link from "next/link";
import { PlusIcon } from "@heroicons/react/24/outline";

export default async function Page() {
  return (
    <div className="w-full">
      <div className="flex w-full items-center justify-between">
        <h1 className={`text-2xl`}>Transactions</h1>
      </div>
      <div className="mt-4 flex items-center justify-between gap-2 md:mt-8">
        <Search placeholder="Search transactions..." />
        <CreateTransaction />
      </div>
      {/*  <Suspense key={query + currentPage} fallback={<InvoicesTableSkeleton />}>
        <Table query={query} currentPage={currentPage} />
      </Suspense> */}
      <Table query={""} currentPage={1} />
      <div className="mt-5 flex w-full justify-center">
        {/* <Pagination totalPages={totalPages} /> */}
      </div>
    </div>
  );
}

export function CreateTransaction() {
  return (
    <Link
      href=""
      className="flex h-10 items-center rounded-lg bg-blue-600 px-4 text-sm font-medium text-white transition-colors hover:bg-blue-500 focus-visible:outline focus-visible:outline-offset-2 focus-visible:outline-blue-600"
    >
      <span className="hidden md:block">Create Transactions</span>{" "}
      <PlusIcon className="h-5 md:ml-4" />
    </Link>
  );
}
