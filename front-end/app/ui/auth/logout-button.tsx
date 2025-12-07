// app/ui/auth/logout-button.tsx
"use client";

import { useRouter } from "next/navigation";
import { PowerIcon } from "@heroicons/react/24/outline";
import { logout } from "@/app/lib/data";

export default function LogoutButton() {
  const router = useRouter();

  const handleLogout = async () => {
    try {
      await logout(); // Axios -> POST /logout
      router.push("/"); // Go home
      router.refresh(); // Re-read cookies / auth on server
    } catch (err) {
      console.error("Logout error:", err);
    }
  };

  return (
    <button
      type="button" // IMPORTANT: not submit
      onClick={handleLogout}
      className="flex h-[48px] w-full grow items-center justify-center gap-2 rounded-md 
                 bg-gray-50 p-3 text-sm font-medium hover:bg-gray-100 hover:text-gray-600
                 md:flex-none md:justify-start md:p-2 md:px-3"
    >
      <PowerIcon className="w-6" />
      <div className="hidden md:block">Sign Out</div>
    </button>
  );
}
