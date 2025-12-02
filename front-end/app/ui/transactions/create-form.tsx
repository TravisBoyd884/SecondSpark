"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { CurrencyDollarIcon, CalendarIcon } from "@heroicons/react/24/outline";
import { Button } from "@/app/ui/button";
import { createTransaction } from "@/app/lib/data";

export default function Form() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    const formData = new FormData(e.currentTarget);

    const saleDate = formData.get("sale_date") as string | null;
    const total = formData.get("total") as string | null;
    const tax = formData.get("tax") as string | null;
    const sellerCommission = formData.get("seller_comission") as string | null;

    if (!saleDate || !total || !tax || !sellerCommission) {
      setError("Please fill out all fields.");
      setIsSubmitting(false);
      return;
    }

    const totalValue = parseFloat(total);
    const taxValue = parseFloat(tax);
    const commissionValue = parseFloat(sellerCommission);

    if ([totalValue, taxValue, commissionValue].some(isNaN)) {
      setError("Total, tax, and commission must be valid numbers.");
      setIsSubmitting(false);
      return;
    }

    try {
      await createTransaction({
        sale_date: saleDate,
        total: totalValue,
        tax: taxValue,
        reseller_comission: commissionValue,
        reseller_id: 1, // TEMP: replace with actual logged-in user ID later
      });

      router.push("/dashboard/transactions");
      router.refresh();
    } catch (err) {
      console.error(err);
      setError("Failed to create transaction.");
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <div className="rounded-md bg-gray-50 p-4 md:p-6">
        {/* Sale Date */}
        <div className="mb-4">
          <label htmlFor="sale_date" className="mb-2 block text-sm font-medium">
            Sale Date
          </label>
          <div className="relative">
            <input
              id="sale_date"
              name="sale_date"
              type="date"
              className="peer block w-full rounded-md border border-gray-200 py-2 pl-10 text-sm"
            />
            <CalendarIcon className="pointer-events-none absolute left-3 top-1/2 h-[18px] w-[18px] -translate-y-1/2 text-gray-500" />
          </div>
        </div>

        {/* Total Amount */}
        <div className="mb-4">
          <label htmlFor="total" className="mb-2 block text-sm font-medium">
            Total Amount
          </label>
          <div className="relative">
            <input
              id="total"
              name="total"
              type="number"
              step="0.01"
              placeholder="Enter total amount"
              className="peer block w-full rounded-md border border-gray-200 py-2 pl-10 text-sm"
            />
            <CurrencyDollarIcon className="pointer-events-none absolute left-3 top-1/2 h-[18px] w-[18px] -translate-y-1/2 text-gray-500" />
          </div>
        </div>

        {/* Tax */}
        <div className="mb-4">
          <label htmlFor="tax" className="mb-2 block text-sm font-medium">
            Total Tax
          </label>
          <div className="relative">
            <input
              id="tax"
              name="tax"
              type="number"
              step="0.01"
              placeholder="Enter tax amount"
              className="peer block w-full rounded-md border border-gray-200 py-2 pl-10 text-sm"
            />
            <CurrencyDollarIcon className="pointer-events-none absolute left-3 top-1/2 h-[18px] w-[18px] -translate-y-1/2 text-gray-500" />
          </div>
        </div>

        {/* Seller Commission */}
        <div className="mb-4">
          <label
            htmlFor="seller_comission"
            className="mb-2 block text-sm font-medium"
          >
            Seller Commission
          </label>
          <div className="relative">
            <input
              id="seller_comission"
              name="seller_comission"
              type="number"
              step="0.01"
              placeholder="Enter commission amount"
              className="peer block w-full rounded-md border border-gray-200 py-2 pl-10 text-sm"
            />
            <CurrencyDollarIcon className="pointer-events-none absolute left-3 top-1/2 h-[18px] w-[18px] -translate-y-1/2 text-gray-500" />
          </div>
        </div>

        {error && (
          <p className="mt-4 text-sm text-red-500" aria-live="polite">
            {error}
          </p>
        )}
      </div>

      {/* Actions */}
      <div className="mt-6 flex justify-end gap-4">
        <Link
          href="/dashboard/transactions"
          className="flex h-10 items-center rounded-lg bg-gray-100 px-4 text-sm font-medium text-gray-600 hover:bg-gray-200"
        >
          Cancel
        </Link>

        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Creating..." : "Create Transaction"}
        </Button>
      </div>
    </form>
  );
}
