import { useEffect } from "react";
import { Organization, User } from "@/app/lib/definitions";
import { useState } from "react";

export default function Page() {
  const [organization, setOrganization] = useState<Organization | null>(null);
  const [users, setUsers] = useState<User[]>([]);

  useEffect(() => {
    getUserOrganization();
    getOrganizationUsers();
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

  const handleUpdateOrganization = async (organization_id: string | undefined) => {
    const response = await fetch("/api/organization", {
      method: "PUT",
      body: JSON.stringify({ organization_id, name: organization?.name }),
    });
  }

  return (
    <div>
      <h1>Organization</h1>
      <div className="flex flex-col gap-2">
        <p className="text-lg font-bold">Name: {organization?.name}</p>
        <p className="text-lg font-bold">ID: {organization?.organization_id}</p>
        <button className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 cursor-pointer" onClick={() => handleUpdateOrganization(organization?.organization_id)}>Update Organization</button>
      </div>
      <div className="flex flex-col gap-2">
        <p className="text-lg font-bold">Users:</p>
        <div className="flex flex-col gap-2">
          {users.map((user) => (
            <p key={user.user_id}>{user.username}</p>
          ))}
        </div>
      </div>
    </div>
  );
}
