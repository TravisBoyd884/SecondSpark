'use client';
import { useState, useEffect } from 'react';
import { Organization } from '@/app/lib/definitions';
import '@/app/dashboard/items/items.css';


interface OrganizationModalProps {
    show: boolean;
    onHide: () => void;
    organization: Organization | null;
    onSave: (updatedOrganization: Partial<Organization>) => void;
}

export default function OrganizationModal({ show, onHide, organization, onSave }: OrganizationModalProps) {
    const [name, setName] = useState('');
    const [organizationId, setOrganizationId] = useState('');

    useEffect(() => {
        if (organization) {
            setName(organization.name || '');
            setOrganizationId(organization.organization_id || '');
        }
    }, [organization]);

    return (
        <div className={`modal ${show ? 'show' : ''} modal-dialog-centered modal-lg`}>
            <div className="modal-header">
                
            </div>
            <div className="modal-content">
                <div className="modal-body flex flex-col gap-4">
                    <div className="flex flex-col gap-2">
                        <label htmlFor="name" className="font-semibold">Organization Name</label>
                        <input
                            id="name"
                            type="text"
                            className="modal-title border border-gray-300 rounded-md px-3 py-2"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                        />
                    </div>
                    {organization && (
                        <div className="flex flex-col gap-2">
                            <label className="font-semibold">Organization ID</label>
                            <p className="text-gray-600">{organizationId}</p>
                        </div>
                    )}
                </div>
                <div className="modal-footer flex justify-center gap-4">
                    <button 
                        className="bg-green-500 text-white px-4 py-2 rounded-md hover:bg-green-600 cursor-pointer" 
                        onClick={() => onSave({
                            name,
                            organization_id: organizationId
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

