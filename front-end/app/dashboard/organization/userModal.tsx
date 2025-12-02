'use client';
import { useState, useEffect } from 'react';
import { User } from '@/app/lib/definitions';
import '@/app/dashboard/items/items.css';

interface UserModalProps {
    show: boolean;
    onHide: () => void;
    user: User | null;
    onSave: (updatedUser: Partial<User>) => void;
}

export default function UserModal({ show, onHide, user, onSave }: UserModalProps) {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [organizationId, setOrganizationId] = useState('');
    const [organizationRole, setOrganizationRole] = useState<'Admin' | 'Member'>('Member');

    useEffect(() => {
        if (user) {
            setUsername(user.username || '');
            setEmail(user.email || '');
            setPassword(user.password || '');
            setOrganizationId(user.organization_id as unknown as string || '');
            setOrganizationRole(user.organization_role as 'Admin' | 'Member');
        }
    }, [user]);

    return (
        <div className={`modal ${show ? 'show' : ''} modal-dialog-centered modal-lg`}>
            <div className="modal-header">
                
            </div>
            <div className="modal-content">
                <div className="modal-body flex flex-col gap-4">
                    <div className="flex flex-col gap-2">
                        <label htmlFor="username" className="font-semibold">Username</label>
                        <input
                            id="username"
                            type="text"
                            className="modal-title border border-gray-300 rounded-md px-3 py-2"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                        />
                    </div>
                    <div className="flex flex-col gap-2">
                        <label htmlFor="email" className="font-semibold">Email</label>
                        <input
                            id="email"
                            type="email"
                            className="border border-gray-300 rounded-md px-3 py-2"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                        />
                    </div>
                    <div className="flex flex-col gap-2">
                        <label htmlFor="password" className="font-semibold">Password</label>
                        <input
                            id="password"
                            type="password"
                            className="border border-gray-300 rounded-md px-3 py-2"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                        />
                    </div>
                    <div className="flex flex-col gap-2">
                        <label htmlFor="organization_id" className="font-semibold">Organization ID</label>
                        <input
                            id="organization_id"
                            type="text"
                            className="border border-gray-300 rounded-md px-3 py-2"
                            value={organizationId}
                            onChange={(e) => setOrganizationId(e.target.value)}
                        />
                    </div>
                    <div className="flex flex-col gap-2">
                        <label htmlFor="organization_role" className="font-semibold">Organization Role</label>
                        <select
                            id="organization_role"
                            className="border border-gray-300 rounded-md px-3 py-2"
                            value={organizationRole}
                            onChange={(e) => setOrganizationRole(e.target.value as 'Admin' | 'Member')}
                        >
                            <option value="Member">Member</option>
                            <option value="Admin">Admin</option>
                        </select>
                    </div>
                    {user && (
                        <div className="flex flex-col gap-2">
                            <label className="font-semibold">User ID</label>
                            <p className="text-gray-600">{user.user_id}</p>
                        </div>
                    )}
                </div>
                <div className="modal-footer flex justify-center gap-4">
                    <button 
                        className="bg-green-500 text-white px-4 py-2 rounded-md hover:bg-green-600 cursor-pointer" 
                        onClick={() => onSave({
                            username,
                            email,
                            password,
                            organization_id: organizationId as unknown as number,
                            organization_role: organizationRole,
                            user_id: user?.user_id
                        })}
                    >
                        Save Changes
                    </button>
                    <button 
                        className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 cursor-pointer" 
                        onClick={onHide}
                    >
                        Close
                    </button>
                </div>
            </div>
        </div>
    );
}

