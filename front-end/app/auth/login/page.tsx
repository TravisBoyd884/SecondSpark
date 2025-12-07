"use client";

import { useState } from "react";
import { login } from "@/app/lib/data";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [msg, setMsg] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setMsg("");

    try {
      const result = await login({
        username,
        password,
      });

      // Show success (optional)
      setMsg("Login successful!");

      // ✅ Only redirect on success
      router.push("/dashboard");
      router.refresh();
    } catch (err: any) {
      console.error("Login error:", err);
      // If we threw an Error with a message (see login() below), use that
      setMsg(
        "Login failed: " +
          (err?.message || err?.response?.data?.error || "Unknown error"),
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-md bg-white shadow-md rounded-lg p-6 space-y-4"
      >
        <h1 className="text-2xl font-semibold text-center">Sign In</h1>

        {msg && (
          <pre className="bg-gray-100 p-2 rounded text-sm text-center whitespace-pre-wrap">
            {msg}
          </pre>
        )}

        <div className="space-y-1">
          <label className="block text-sm font-medium">Username</label>
          <input
            className="w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-black"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="your_username"
            required
          />
        </div>

        <div className="space-y-1">
          <label className="block text-sm font-medium">Password</label>
          <input
            className="w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-black"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            type="password"
            placeholder="••••••••"
            required
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-2 rounded bg-black text-white hover:bg-opacity-90 disabled:opacity-60"
        >
          {loading ? "Signing In..." : "Sign In"}
        </button>
      </form>
    </div>
  );
}
