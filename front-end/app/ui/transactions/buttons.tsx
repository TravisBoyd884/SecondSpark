// app/ui/transactions/buttons.tsx
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { TrashIcon } from "@heroicons/react/24/outline";
import { deleteTransaction } from "@/app/lib/data";

export function DeleteInvoice({ id }: { id: string }) {
  const router = useRouter();
  const [isDeleting, setIsDeleting] = useState(false);

  async function handleDelete(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();

    if (isDeleting) return;

    const confirmed = window.confirm(
      "Are you sure you want to delete this transaction?",
    );
    if (!confirmed) return;

    setIsDeleting(true);
    try {
      await deleteTransaction(Number(id));
      router.refresh(); // reload data for the table
    } catch (err) {
      console.error(err);
      window.alert("Failed to delete transaction.");
    } finally {
      setIsDeleting(false);
    }
  }

  return (
    <form onSubmit={handleDelete}>
      <button
        type="submit"
        className="rounded-md border p-2 hover:bg-gray-100 disabled:opacity-50"
        disabled={isDeleting}
      >
        <span className="sr-only">Delete</span>
        <TrashIcon className="w-5" />
      </button>
    </form>
  );
}
