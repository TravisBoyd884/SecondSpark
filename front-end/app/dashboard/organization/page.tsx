"use client";
import { useEffect } from "react";
import { Organization, User } from "@/app/lib/definitions";
import { useState } from "react";
import UserModal from "./userModal";
import OrganizationModal from "./organizationModal";
import { organizations, users } from '@/app/lib/placeholder-data';

export default function Page() {
  const [organization, setOrganization] = useState<Organization | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [selectedOrganization, setSelectedOrganization] = useState<Organization | null>(null);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [showUserModal, setShowUserModal] = useState(false);
  const [showOrganizationModal, setShowOrganizationModal] = useState(false);

  useEffect(() => {
    getUserOrganization();
    getOrganizationUsers();
    setOrganization(organizations[0]);
    setUsers(users);
    setSelectedOrganization(organizations[0]);
  }, []);

  const getUserOrganization = async () => {
    const response = await fetch("/api/organization");
    const data = await response.json();
    console.log(data);
    setOrganization(data);
  }

  const getOrganizationUsers = async () => {
    const response = await fetch("/api/users");
    const data = await response.json();
    console.log(data);
    setUsers(data);
  }

  const handleViewUser = (user: User) => {
    setSelectedUser(user);
  }

  const handleCloseUserModal = () => {
    setSelectedUser(null);
  }

  const handleUpdateOrganization = async (updatedOrganization: Partial<Organization>) => {
    setSelectedOrganization(updatedOrganization as Organization);
    setShowOrganizationModal(true);
  }

  const handleDeleteUser = async (user_id: string) => {
    const response = await fetch("/api/users", {
      method: "DELETE",
      body: JSON.stringify({ user_id }),
    });
  }

  const handleUpdateUser = async (updatedUser: Partial<User>) => {
    setSelectedUser(updatedUser as User);
    setShowUserModal(true);
  }

  const handleCloseOrganizationModal = () => {
    setSelectedOrganization(null);
    setShowOrganizationModal(false);
  }

  return (
    <div>
      <h1>Organization</h1>
      <div className="flex flex-col padding-20 gap-2">
        <p className="text-lg font-bold">Name: {organization?.name}</p>
        <p className="text-lg font-bold">ID: {organization?.organization_id}</p>
      </div>
      <button className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 cursor-pointer" onClick={() => handleUpdateOrganization(selectedOrganization as Organization)}>Update Organization</button>
      <div className="flex flex-col gap-2">
        <p className="text-lg font-bold">Users:</p>
        <div className="flex flex-col gap-2">
          {users.map((user) => (
            <div className="flex flex-row gap-2">
              <p key={user.user_id}>{user.username}</p>
              <button className="bg-red-500 text-white px-4 py-2 rounded-md hover:bg-red-600 cursor-pointer" onClick={() => handleDeleteUser(user.user_id)}>Delete User</button>
              <button className="bg-green-500 text-white px-4 py-2 rounded-md hover:bg-green-600 cursor-pointer" onClick={() => handleUpdateUser(user as User)}>Update User</button>
            </div>
          ))}
        </div>
      </div>
      <UserModal show={showUserModal} onHide={handleCloseUserModal} user={selectedUser} onSave={handleUpdateUser} />
      <OrganizationModal show={showOrganizationModal} onHide={handleCloseOrganizationModal} organization={selectedOrganization} onSave={handleUpdateOrganization} />
    </div>
  );
}
