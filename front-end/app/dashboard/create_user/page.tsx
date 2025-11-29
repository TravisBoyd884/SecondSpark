"use client";

import { useState } from "react";
import { createUser } from "@/app/lib/data";

export default function RegisterPage() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [organizationId, setOrganizationId] = useState<string>("");
  const [organizationRole, setOrganizationRole] = useState("");
  const [ebayAccountId, setEbayAccountId] = useState<string>("");
  const [etsyAccountId, setEtsyAccountId] = useState<string>("");

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setLoading(true);
    setMessage(null);
    setError(null);

    try {
      const result = await createUser({
        username,
        password,
        email,
        organization_id:
          organizationId.trim() === "" ? null : Number(organizationId),
        organization_role:
          organizationRole.trim() === "" ? null : organizationRole,
        ebay_account_id:
          ebayAccountId.trim() === "" ? null : Number(ebayAccountId),
        etsy_account_id:
          etsyAccountId.trim() === "" ? null : Number(etsyAccountId),
      });

      if ((result as any).error) {
        setError((result as any).error);
      } else {
        setMessage("User created successfully");
        // optional: clear form
        setUsername("");
        setEmail("");
        setPassword("");
        setOrganizationId("");
        setOrganizationRole("");
        setEbayAccountId("");
        setEtsyAccountId("");
      }
    } catch (err) {
      setError("Something went wrong creating the user");
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
        <h1 className="text-2xl font-semibold text-center">Create User</h1>

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

        {/* Optional fields */}
        <div className="space-y-1">
          <label className="block text-sm">Organization ID (optional)</label>
          <input
            className="w-full border px-3 py-2 rounded"
            value={organizationId}
            onChange={(e) => setOrganizationId(e.target.value)}
            placeholder="e.g. 1"
          />
        </div>

        <div className="space-y-1">
          <label className="block text-sm">Organization Role (optional)</label>
          <input
            className="w-full border px-3 py-2 rounded"
            value={organizationRole}
            onChange={(e) => setOrganizationRole(e.target.value)}
            placeholder="e.g. admin"
          />
        </div>

        <div className="space-y-1">
          <label className="block text-sm">eBay Account ID (optional)</label>
          <input
            className="w-full border px-3 py-2 rounded"
            value={ebayAccountId}
            onChange={(e) => setEbayAccountId(e.target.value)}
            placeholder="e.g. 42"
          />
        </div>

        <div className="space-y-1">
          <label className="block text-sm">Etsy Account ID (optional)</label>
          <input
            className="w-full border px-3 py-2 rounded"
            value={etsyAccountId}
            onChange={(e) => setEtsyAccountId(e.target.value)}
            placeholder="e.g. 7"
          />
        </div>

        <button
          type="submit"
          className="w-full py-2 rounded bg-black text-white disabled:opacity-60"
          disabled={loading}
        >
          {loading ? "Creating..." : "Create User"}
        </button>
      </form>
    </div>
  );
}
