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
    setShowUserModal(false);
  }

  const handleOpenOrganizationModal = () => {
    setSelectedOrganization(organization);
    setShowOrganizationModal(true);
  }

  const handleSaveOrganization = async (updatedOrganization: Partial<Organization>) => {
    if (!updatedOrganization.organization_id || !updatedOrganization.name) {
      console.error("Organization ID and name are required");
      return;
    }

    // Convert organization_id to integer if it's a string (backend expects int)
    const orgId = typeof updatedOrganization.organization_id === 'string' 
      ? parseInt(updatedOrganization.organization_id) 
      : updatedOrganization.organization_id;

    if (isNaN(orgId as number)) {
      console.error("Invalid organization ID");
      alert("Invalid organization ID");
      return;
    }

    try {
      const response = await fetch(`/api/organizations/${orgId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: updatedOrganization.name,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error("Failed to update organization:", errorData);
        alert(`Failed to update organization: ${errorData.error || "Unknown error"}`);
        return;
      }

      const data = await response.json();
      console.log("Organization updated successfully:", data);
      
      // Update local state
      setOrganization(data);
      setSelectedOrganization(data);
      setShowOrganizationModal(false);
      
      // Refresh the organization data
      getUserOrganization();
    } catch (error) {
      console.error("Error updating organization:", error);
      alert("An error occurred while updating the organization");
    }
  }

  const handleDeleteUser = async (user_id: string) => {
    // Convert user_id to integer if it's a string (backend expects int)
    const userId = typeof user_id === 'string' ? parseInt(user_id) : user_id;
    
    if (isNaN(userId as number)) {
      console.error("Invalid user ID");
      alert("Invalid user ID");
      return;
    }

    try {
      const response = await fetch(`/api/users/${userId}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error("Failed to delete user:", errorData);
        alert(`Failed to delete user: ${errorData.error || "Unknown error"}`);
        return;
      }

      // Remove user from local state
      setUsers(users.filter(user => user.user_id !== user_id));
    } catch (error) {
      console.error("Error deleting user:", error);
      alert("An error occurred while deleting the user");
    }
  }

  const handleOpenUserModal = (user: User) => {
    setSelectedUser(user);
    setShowUserModal(true);
  }

  const handleSaveUser = async (updatedUser: Partial<User>) => {
    if (!updatedUser.user_id) {
      console.error("User ID is required");
      return;
    }

    // Convert user_id to integer if it's a string (backend expects int)
    const userId = typeof updatedUser.user_id === 'string' 
      ? parseInt(updatedUser.user_id) 
      : updatedUser.user_id;

    if (isNaN(userId as number)) {
      console.error("Invalid user ID");
      alert("Invalid user ID");
      return;
    }

    try {
      const response = await fetch(`/api/users/${userId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          organization_role: updatedUser.organization_role,
          organization_id: updatedUser.organization_id ? parseInt(updatedUser.organization_id) : undefined,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error("Failed to update user:", errorData);
        alert(`Failed to update user: ${errorData.error || "Unknown error"}`);
        return;
      }

      const data = await response.json();
      console.log("User updated successfully:", data);
      
      // Update local state
      setUsers(users.map(user => 
        user.user_id === updatedUser.user_id 
          ? { ...user, ...updatedUser }
          : user
      ));
      setSelectedUser(null);
      setShowUserModal(false);
      
      // Refresh the users data
      getOrganizationUsers();
    } catch (error) {
      console.error("Error updating user:", error);
      alert("An error occurred while updating the user");
    }
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
      <button className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 cursor-pointer" onClick={handleOpenOrganizationModal}>Update Organization</button>
      <div className="flex flex-col gap-2">
        <p className="text-lg font-bold">Users:</p>
        <div className="flex flex-col gap-2">
          {users.map((user) => (
            <div className="flex flex-row gap-2">
              <p key={user.user_id}>{user.username}</p>
              <button className="bg-red-500 text-white px-4 py-2 rounded-md hover:bg-red-600 cursor-pointer" onClick={() => handleDeleteUser(user.user_id)}>Delete User</button>
              <button className="bg-green-500 text-white px-4 py-2 rounded-md hover:bg-green-600 cursor-pointer" onClick={() => handleOpenUserModal(user)}>Update User</button>
            </div>
          ))}
        </div>
      </div>
      <UserModal show={showUserModal} onHide={handleCloseUserModal} user={selectedUser} onSave={handleSaveUser} />
      <OrganizationModal show={showOrganizationModal} onHide={handleCloseOrganizationModal} organization={selectedOrganization} onSave={handleSaveOrganization} />
    </div>
  );
}
