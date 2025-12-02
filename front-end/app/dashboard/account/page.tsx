import {
  User,
  Mail,
  Building2,
  Shield,
  Calendar,
  Package,
  DollarSign,
  Clock,
} from "lucide-react";
import { getUserById, getUserStats } from "@/app/lib/data";

function formatDate(dateStr: string | null): string {
  if (!dateStr) return "N/A";
  const d = new Date(dateStr);
  if (isNaN(d.getTime())) return dateStr;
  return d.toLocaleDateString(undefined, {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

function formatCurrency(amount: number): string {
  return amount.toLocaleString(undefined, {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 2,
  });
}

export default async function Page() {
  const userId = 1; // replace w/ auth later

  const [user, stats] = await Promise.all([
    getUserById(userId),
    getUserStats(userId),
  ]);

  const memberSince = null; // no created_at yet
  const orgName =
    user.organization_id !== null
      ? `Organization #${user.organization_id}`
      : "No organization";
  const role = user.organization_role ?? "member";

  return (
    <div className="bg-gray-50 max-h-screen w-full p-8">
      {/* HEADER */}
      <div className="mb-10">
        <h1 className="text-3xl font-semibold text-gray-900">Account</h1>
        <p className="text-sm text-gray-500">Manage your profile & activity</p>
      </div>

      {/* GRID LAYOUT THAT FILLS FULL PAGE WIDTH */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 w-full">
        {/* LEFT SIDE: PROFILE CARD (2/3 of screen) */}
        <div className="lg:col-span-2 bg-white border border-gray-200 rounded-xl p-8 shadow-sm w-full">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">
            Profile Information
          </h2>

          <div className="flex items-center gap-6 mb-8">
            <div className="w-20 h-20 rounded-full bg-gray-900 text-white flex items-center justify-center">
              <User className="w-10 h-10" />
            </div>
            <div>
              <p className="text-lg font-semibold text-gray-900">
                {user.username}
              </p>
              <p className="text-gray-500">{user.email}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-12 gap-y-6 text-sm">
            <div>
              <p className="text-gray-500 flex items-center gap-2 mb-1">
                <Building2 className="w-4 h-4" />
                Organization
              </p>
              <p className="font-medium text-gray-900">{orgName}</p>
            </div>

            <div>
              <p className="text-gray-500 flex items-center gap-2 mb-1">
                <Shield className="w-4 h-4" />
                Role
              </p>
              <span className="inline-flex px-3 py-1 bg-gray-100 rounded-full text-xs font-medium text-gray-700">
                {role}
              </span>
            </div>

            <div>
              <p className="text-gray-500 flex items-center gap-2 mb-1">
                <Calendar className="w-4 h-4" />
                Member Since
              </p>
              <p className="font-medium text-gray-900">
                {memberSince ? formatDate(memberSince) : "N/A"}
              </p>
            </div>
          </div>
        </div>

        {/* RIGHT SIDE: OVERVIEW CARD */}
        <div className="bg-white border border-gray-200 rounded-xl p-8 shadow-sm w-full">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">
            Account Overview
          </h2>

          <div className="space-y-6">
            {/* Total Transactions */}
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-gray-900 text-white rounded-lg flex items-center justify-center">
                <Package className="w-5 h-5" />
              </div>
              <div>
                <p className="text-gray-500 text-sm">Total Transactions</p>
                <p className="text-lg font-semibold text-gray-900">
                  {stats.totalTransactions}
                </p>
              </div>
            </div>

            {/* Total Value */}
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-gray-900 text-white rounded-lg flex items-center justify-center">
                <DollarSign className="w-5 h-5" />
              </div>
              <div>
                <p className="text-gray-500 text-sm">Total Value</p>
                <p className="text-lg font-semibold text-gray-900">
                  {formatCurrency(stats.totalValue)}
                </p>
              </div>
            </div>

            {/* Last Activity */}
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-gray-900 text-white rounded-lg flex items-center justify-center">
                <Clock className="w-5 h-5" />
              </div>
              <div>
                <p className="text-gray-500 text-sm">Last Activity</p>
                <p className="text-lg font-semibold text-gray-900">
                  {stats.lastActivity
                    ? formatDate(stats.lastActivity)
                    : "No activity yet"}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* NOTIFICATION PREFERENCES FULL WIDTH BELOW */}
      <div className="bg-white border border-gray-200 rounded-xl p-8 shadow-sm mt-10 w-full">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">
          Notification Preferences
        </h2>

        <div className="space-y-6 text-sm">
          <label className="flex items-center justify-between">
            <div>
              <p className="font-medium text-gray-900">
                Email notifications for new transactions
              </p>
              <p className="text-gray-500 text-xs">
                Get notified when new transactions are added.
              </p>
            </div>
            <input type="checkbox" defaultChecked className="w-5 h-5" />
          </label>

          <label className="flex items-center justify-between">
            <div>
              <p className="font-medium text-gray-900">Low inventory alerts</p>
              <p className="text-gray-500 text-xs">
                Receive alerts when items are running low.
              </p>
            </div>
            <input type="checkbox" defaultChecked className="w-5 h-5" />
          </label>

          <label className="flex items-center justify-between">
            <div>
              <p className="font-medium text-gray-900">
                Weekly summary reports
              </p>
              <p className="text-gray-500 text-xs">
                Get weekly summaries of activity.
              </p>
            </div>
            <input type="checkbox" className="w-5 h-5" />
          </label>

          <label className="flex items-center justify-between">
            <div>
              <p className="font-medium text-gray-900">System updates</p>
              <p className="text-gray-500 text-xs">
                Stay informed about new features and updates.
              </p>
            </div>
            <input type="checkbox" defaultChecked className="w-5 h-5" />
          </label>
        </div>
      </div>
    </div>
  );
}
