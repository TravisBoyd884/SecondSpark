"use client";
import { useEffect } from "react";
import { Organization, User } from "@/app/lib/definitions";
import { useState } from "react";
import UserModal from "./userModal";
import OrganizationModal from "./organizationModal";
import { organizations, users } from '@/app/lib/placeholder-data';

export default function Page() {
  const [organization, setOrganization] = useState<Organization | null>(null);
  const [organizationId, setOrganizationId] = useState<string>('');
  const [usersList, setUsersList] = useState<User[]>([]);
  const [selectedOrganization, setSelectedOrganization] = useState<Organization | null>(null);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [showUserModal, setShowUserModal] = useState(false);
  const [showOrganizationModal, setShowOrganizationModal] = useState(false);

  useEffect(() => {
    const orgId = "2";
    setOrganizationId(orgId);
    getUserOrganization(orgId);
    getOrganizationUsers(orgId);
  }, []);

  const getUserOrganization = async (id: string) => {
    if (!id) {
      console.error('Organization ID is required');
      return;
    }

    try {
      const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
      const response = await fetch(`${apiBaseUrl}/organizations/${id}`);
      if (!response.ok) {
        console.error('Failed to fetch organization');
        return;
      }
      const data = await response.json();
      console.log(data);
      setOrganization(data);
      setOrganizationId(data.organization_id);
    } catch (error) {
      console.error('Error fetching organization:', error);
    }
  }

  const getOrganizationUsers = async (id: string) => {
    if (!id) {
      console.error('Organization ID is required');
      return;
    }

    try {
      const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
      const response = await fetch(`${apiBaseUrl}/organizations/${id}/users`);
      if (!response.ok) {
        console.error('Failed to fetch users');
        return;
      }
      const data = await response.json();
      console.log(data);
      setUsersList(data);
    } catch (error) {
      console.error('Error fetching users:', error);
    }
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
      const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
      const response = await fetch(`${apiBaseUrl}/organizations/${orgId}`, {
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
      
      // Refresh the organization data and users
      getUserOrganization(orgId.toString());
      getOrganizationUsers(orgId.toString());
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
      const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
      const response = await fetch(`${apiBaseUrl}/users/${userId}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error("Failed to delete user:", errorData);
        alert(`Failed to delete user: ${errorData.error || "Unknown error"}`);
        return;
      }

      // Remove user from local state
      setUsersList(usersList.filter(user => user.user_id !== user_id));
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
      // Prepare the update payload with all fields from the modal
      const updatePayload: any = {};
      
      if (updatedUser.email !== undefined) {
        updatePayload.email = updatedUser.email;
      }
      if (updatedUser.password !== undefined) {
        updatePayload.password = updatedUser.password;
      }
      if (updatedUser.organization_role !== undefined) {
        updatePayload.organization_role = updatedUser.organization_role;
      }
      if (updatedUser.organization_id !== undefined) {
        updatePayload.organization_id = typeof updatedUser.organization_id === 'string' 
          ? parseInt(updatedUser.organization_id) 
          : updatedUser.organization_id;
      }
      
      const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
      const response = await fetch(`${apiBaseUrl}/users/${userId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(updatePayload),
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
      setUsersList(usersList.map(user => 
        user.user_id === updatedUser.user_id 
          ? { ...user, ...updatedUser }
          : user
      ));
      setSelectedUser(null);
      setShowUserModal(false);
      
      // Refresh the users data
      if (organizationId) {
        getOrganizationUsers(organizationId);
      }
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
      <h1 className="text-2xl font-bold text-center mb-4">Organization</h1>
      <div className="flex flex-col padding-20 gap-2">
        <p className="text-lg font-bold">Name: {organization?.name}</p>
        <p className="text-lg font-bold">ID: {organization?.organization_id}</p>
      </div>
      <button className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 cursor-pointer" onClick={handleOpenOrganizationModal}>Update Organization</button>
      <div className="flex flex-col gap-2 mt-4">
        <p className="text-lg font-bold">Users:</p>
        <div className="overflow-x-auto">
          <table className="w-full bg-gray-100 border-collapse">
            <thead>
              <tr className="bg-gray-200">
                <th className="border border-gray-300 px-4 py-2 text-left">Username</th>
                <th className="border border-gray-300 px-4 py-2 text-left">Email</th>
                <th className="border border-gray-300 px-4 py-2 text-left">Role</th>
                <th className="border border-gray-300 px-4 py-2 text-left">Actions</th>
              </tr>
            </thead>
            <tbody>
              {usersList.map((user) => (
                <tr key={user.user_id} className="bg-gray-50 hover:bg-gray-100">
                  <td className="border border-gray-300 px-4 py-2">{user.username}</td>
                  <td className="border border-gray-300 px-4 py-2">{user.email}</td>
                  <td className="border border-gray-300 px-4 py-2">{user.organization_role}</td>
                  <td className="border border-gray-300 px-4 py-2">
                    <div className="flex gap-4 justify-start">
                      <button className="bg-black text-white px-6 py-2 rounded-md hover:bg-gray-800 cursor-pointer" onClick={() => handleDeleteUser(user.user_id)}>Delete User</button>
                      <button className="bg-white text-black border border-gray-300 px-6 py-2 rounded-md hover:bg-green-600 cursor-pointer" onClick={() => handleOpenUserModal(user)}>Update User</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      <UserModal show={showUserModal} onHide={handleCloseUserModal} user={selectedUser} onSave={handleSaveUser} />
      <OrganizationModal show={showOrganizationModal} onHide={handleCloseOrganizationModal} organization={selectedOrganization} onSave={handleSaveOrganization} />
    </div>
  );
}
