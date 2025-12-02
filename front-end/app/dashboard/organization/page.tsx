"use client";

import { useEffect, useState } from "react";
import { Organization, User } from "@/app/lib/definitions";
import UserModal from "./userModal";
import OrganizationModal from "./organizationModal";

import {
  fetchFirstOrganization,
  fetchOrganizationUsers,
  updateOrganizationApi,
  deleteUserApi,
  updateUserApi,
} from "@/app/lib/data";

export default function OrganizationPage() {
  const [organization, setOrganization] = useState<Organization | null>(null);
  const [usersList, setUsersList] = useState<User[]>([]);
  const [selectedOrganization, setSelectedOrganization] =
    useState<Organization | null>(null);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [showUserModal, setShowUserModal] = useState(false);
  const [showOrganizationModal, setShowOrganizationModal] = useState(false);

  // Initial load: organization + its users
  useEffect(() => {
    const load = async () => {
      try {
        const org = await fetchFirstOrganization();
        if (!org) {
          console.error("No organizations found");
          return;
        }

        setOrganization(org);
        setSelectedOrganization(org);

        const users = await fetchOrganizationUsers(org.organization_id);
        setUsersList(users);
      } catch (err) {
        console.error("Error loading organization/users:", err);
      }
    };

    load();
  }, []);

  const handleOpenOrganizationModal = () => {
    if (organization) {
      setSelectedOrganization(organization);
      setShowOrganizationModal(true);
    }
  };

  const handleCloseOrganizationModal = () => {
    setSelectedOrganization(null);
    setShowOrganizationModal(false);
  };

  const handleSaveOrganization = async (
    updatedOrganization: Partial<Organization>,
  ) => {
    if (!updatedOrganization.organization_id || !updatedOrganization.name) {
      console.error("Organization ID and name are required");
      return;
    }

    const orgId =
      typeof updatedOrganization.organization_id === "string"
        ? parseInt(updatedOrganization.organization_id as unknown as string)
        : (updatedOrganization.organization_id as number);

    if (isNaN(orgId)) {
      console.error("Invalid organization ID");
      alert("Invalid organization ID");
      return;
    }

    try {
      const data = await updateOrganizationApi(orgId, {
        name: updatedOrganization.name,
      });

      // ✅ Keep showing the org we just updated
      setOrganization(data);
      setSelectedOrganization(data);
      setShowOrganizationModal(false);
    } catch (error: any) {
      console.error("Error updating organization:", error);
      alert(
        `Failed to update organization: ${
          error?.response?.data?.error || "Unknown error"
        }`,
      );
    }
  };

  const handleOpenUserModal = (user: User) => {
    setSelectedUser(user);
    setShowUserModal(true);
  };

  const handleCloseUserModal = () => {
    setSelectedUser(null);
    setShowUserModal(false);
  };

  const handleDeleteUser = async (user_id: string | number) => {
    const userId =
      typeof user_id === "string" ? parseInt(user_id) : (user_id as number);

    if (isNaN(userId)) {
      console.error("Invalid user ID");
      alert("Invalid user ID");
      return;
    }

    try {
      await deleteUserApi(userId);
      setUsersList((prev) => prev.filter((u) => u.user_id !== user_id));
    } catch (error: any) {
      console.error("Error deleting user:", error);
      alert(
        `Failed to delete user: ${
          error?.response?.data?.error || "Unknown error"
        }`,
      );
    }
  };

  const handleSaveUser = async (updatedUser: Partial<User>) => {
    if (!updatedUser.user_id) {
      console.error("User ID is required");
      return;
    }

    const userId =
      typeof updatedUser.user_id === "string"
        ? parseInt(updatedUser.user_id as unknown as string)
        : (updatedUser.user_id as number);

    if (isNaN(userId)) {
      console.error("Invalid user ID");
      alert("Invalid user ID");
      return;
    }

    const updatePayload: Partial<User> = {};

    if (updatedUser.email !== undefined) {
      updatePayload.email = updatedUser.email;
    }
    if ((updatedUser as any).password !== undefined) {
      // only if your backend accepts password changes here
      (updatePayload as any).password = (updatedUser as any).password;
    }
    if (updatedUser.organization_role !== undefined) {
      updatePayload.organization_role = updatedUser.organization_role;
    }
    if (updatedUser.organization_id !== undefined) {
      updatePayload.organization_id =
        typeof updatedUser.organization_id === "string"
          ? parseInt(updatedUser.organization_id as unknown as string)
          : updatedUser.organization_id;
    }

    try {
      const savedUser = await updateUserApi(userId, updatePayload);

      setUsersList((prev) =>
        prev.map((u) =>
          u.user_id === updatedUser.user_id ? { ...u, ...savedUser } : u,
        ),
      );
      setSelectedUser(null);
      setShowUserModal(false);
    } catch (error: any) {
      console.error("Error updating user:", error);
      alert(
        `Failed to update user: ${
          error?.response?.data?.error || "Unknown error"
        }`,
      );
    }
  };

  return (
    <div>
      <h1>Organization</h1>
      <div className="flex flex-col padding-20 gap-2">
        <p className="text-lg font-bold">Name: {organization?.name}</p>
        <p className="text-lg font-bold">ID: {organization?.organization_id}</p>
      </div>

      <button
        className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 cursor-pointer"
        onClick={handleOpenOrganizationModal}
      >
        Update Organization
      </button>

      <div className="flex flex-col gap-2 mt-4">
        <p className="text-lg font-bold">Users:</p>
        <div className="overflow-x-auto">
          <table className="w-full bg-gray-100 border-collapse">
            <thead>
              <tr className="bg-gray-200">
                <th className="border border-gray-300 px-4 py-2 text-left">
                  Username
                </th>
                <th className="border border-gray-300 px-4 py-2 text-left">
                  Email
                </th>
                <th className="border border-gray-300 px-4 py-2 text-left">
                  Role
                </th>
                <th className="border border-gray-300 px-4 py-2 text-left">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody>
              {usersList.map((user) => (
                <tr key={user.user_id} className="bg-gray-50 hover:bg-gray-100">
                  <td className="border border-gray-300 px-4 py-2">
                    {user.username}
                  </td>
                  <td className="border border-gray-300 px-4 py-2">
                    {user.email}
                  </td>
                  <td className="border border-gray-300 px-4 py-2">
                    {user.organization_role}
                  </td>
                  <td className="border border-gray-300 px-4 py-2">
                    <div className="flex gap-4 justify-start">
                      <button
                        className="bg-black text-white px-6 py-2 rounded-md hover:bg-gray-800 cursor-pointer"
                        onClick={() => handleDeleteUser(user.user_id)}
                      >
                        Delete User
                      </button>
                      <button
                        className="bg-white text-black border border-gray-300 px-6 py-2 rounded-md hover:bg-green-600 cursor-pointer"
                        onClick={() => handleOpenUserModal(user)}
                      >
                        Update User
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <UserModal
        show={showUserModal}
        onHide={handleCloseUserModal}
        user={selectedUser}
        onSave={handleSaveUser}
      />
      <OrganizationModal
        show={showOrganizationModal}
        onHide={handleCloseOrganizationModal}
        organization={selectedOrganization}
        onSave={handleSaveOrganization}
      />
    </div>
  );
}
