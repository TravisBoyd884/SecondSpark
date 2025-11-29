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
import { login } from "@/app/lib/data";

export default function Page() {
  return (
    <div className="flex bg-white mb-8">
      <div className="flex-1 p-8">
        <div className="flex justify-start mb-8">
          <h1>Account</h1>
        </div>

        <div className="space-y-6">
          {/* Profile Section */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h2 className="mb-6">Profile Information</h2>

            <div className="flex items-center gap-6 mb-6">
              <div className="w-24 h-24 bg-black rounded-full flex items-center justify-center text-white">
                <User className="w-12 h-12" />
              </div>
              <div>
                <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100 transition-colors">
                  Change Photo
                </button>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-6">
              <div>
                <label className="block text-gray-600 mb-2 flex items-center gap-2">
                  <User className="w-4 h-4" />
                  Username
                </label>
                <input
                  type="text"
                  defaultValue="john_doe"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black"
                />
              </div>

              <div>
                <label className="block text-gray-600 mb-2 flex items-center gap-2">
                  <Mail className="w-4 h-4" />
                  Email
                </label>
                <input
                  type="email"
                  defaultValue="john.doe@secondspark.com"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black"
                />
              </div>

              <div>
                <label className="block text-gray-600 mb-2 flex items-center gap-2">
                  <Building2 className="w-4 h-4" />
                  Company
                </label>
                <input
                  type="text"
                  defaultValue="SecondSpark"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black"
                />
              </div>

              <div>
                <label className="block text-gray-600 mb-2 flex items-center gap-2">
                  <Shield className="w-4 h-4" />
                  Role
                </label>
                <select
                  defaultValue="manager"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black"
                >
                  <option value="admin">Administrator</option>
                  <option value="manager">Manager</option>
                  <option value="staff">Staff</option>
                  <option value="viewer">Viewer</option>
                </select>
              </div>

              <div className="col-span-2">
                <label className="block text-gray-600 mb-2 flex items-center gap-2">
                  <Calendar className="w-4 h-4" />
                  Member Since
                </label>
                <input
                  type="text"
                  defaultValue="January 15, 2024"
                  disabled
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-600"
                />
              </div>
            </div>
          </div>

          {/* Account Statistics */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h2 className="mb-6">Account Statistics</h2>

            <div className="grid grid-cols-3 gap-6">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-black rounded-lg flex items-center justify-center text-white">
                  <Package className="w-6 h-6" />
                </div>
                <div>
                  <p className="text-gray-600">Total Transactions</p>
                  <p>33</p>
                </div>
              </div>

              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-black rounded-lg flex items-center justify-center text-white">
                  <DollarSign className="w-6 h-6" />
                </div>
                <div>
                  <p className="text-gray-600">Total Value</p>
                  <p>$3609.74</p>
                </div>
              </div>

              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-black rounded-lg flex items-center justify-center text-white">
                  <Clock className="w-6 h-6" />
                </div>
                <div>
                  <p className="text-gray-600">Last Activity</p>
                  <p>2 hours ago</p>
                </div>
              </div>
            </div>
          </div>

          {/* Notification Preferences */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h2 className="mb-6">Notification Preferences</h2>

            <div className="space-y-4">
              <label className="flex items-center justify-between">
                <div>
                  <p>Email notifications for new transactions</p>
                  <p className="text-gray-600 text-sm">
                    Get notified when new transactions are added
                  </p>
                </div>
                <input
                  type="checkbox"
                  defaultChecked
                  className="w-5 h-5 rounded border-gray-300"
                />
              </label>

              <label className="flex items-center justify-between">
                <div>
                  <p>Low inventory alerts</p>
                  <p className="text-gray-600 text-sm">
                    Receive alerts when items are running low
                  </p>
                </div>
                <input
                  type="checkbox"
                  defaultChecked
                  className="w-5 h-5 rounded border-gray-300"
                />
              </label>

              <label className="flex items-center justify-between">
                <div>
                  <p>Weekly summary reports</p>
                  <p className="text-gray-600 text-sm">
                    Get weekly summaries of your inventory activity
                  </p>
                </div>
                <input
                  type="checkbox"
                  className="w-5 h-5 rounded border-gray-300"
                />
              </label>

              <label className="flex items-center justify-between">
                <div>
                  <p>System updates</p>
                  <p className="text-gray-600 text-sm">
                    Stay informed about new features and updates
                  </p>
                </div>
                <input
                  type="checkbox"
                  defaultChecked
                  className="w-5 h-5 rounded border-gray-300"
                />
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
