"use client";

import { useState } from "react";
import { createUser } from "@/app/lib/data";
import { RegisterResponse } from "@/app/lib/definitions";

export default function Page() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [organizationId, setOrganizationId] = useState<string>("");

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setLoading(true);
    setMessage(null);
    setError(null);

    const orgIdNumber = Number(organizationId);
    if (!organizationId.trim() || Number.isNaN(orgIdNumber)) {
      setError("Organization ID must be a valid number");
      setLoading(false);
      return;
    }

    try {
      const result: RegisterResponse = await createUser({
        username,
        password,
        email,
        organization_id: orgIdNumber,
      });

      if (result.error) {
        setError(result.error);
      } else {
        const msg = result.message || "User registered successfully";
        const userId =
          result.user_id !== undefined ? ` (ID: ${result.user_id})` : "";
        setMessage(msg + userId);

        // Clear form
        setUsername("");
        setEmail("");
        setPassword("");
        setOrganizationId("");
      }
    } catch (err) {
      setError("Something went wrong registering the user");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-md space-y-4 border p-6 rounded-lg"
      >
        <h1 className="text-2xl font-semibold text-center">Register</h1>

        {message && (
          <div className="text-green-600 text-sm text-center">{message}</div>
        )}
        {error && (
          <div className="text-red-600 text-sm text-center">{error}</div>
        )}

        <div className="space-y-1">
          <label className="block text-sm">Username</label>
          <input
            className="w-full border px-3 py-2 rounded"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>

        <div className="space-y-1">
          <label className="block text-sm">Email</label>
          <input
            className="w-full border px-3 py-2 rounded"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>

        <div className="space-y-1">
          <label className="block text-sm">Password</label>
          <input
            className="w-full border px-3 py-2 rounded"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>

        <div className="space-y-1">
          <label className="block text-sm">Organization ID</label>
          <input
            className="w-full border px-3 py-2 rounded"
            value={organizationId}
            onChange={(e) => setOrganizationId(e.target.value)}
            placeholder="e.g. 1"
            required
          />
        </div>

        <button
          type="submit"
          className="w-full py-2 rounded bg-black text-white disabled:opacity-60"
          disabled={loading}
        >
          {loading ? "Registering..." : "Register"}
        </button>
      </form>
    </div>
  );
}
