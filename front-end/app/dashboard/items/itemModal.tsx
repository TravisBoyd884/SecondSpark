'use client';
import Button from 'react-bootstrap/Button'
import { Item } from '@/app/lib/definitions';  
import '@/app/dashboard/items/items.css';
interface ItemModalProps {
    show: boolean;
    onHide: () => void;
    item: Item | null;
    onDelete: () => void;
}

export default function ItemModal({ show, onHide, item, onDelete }: ItemModalProps) {
    return (
        <div className={`modal ${show ? 'show' : ''} modal-dialog-centered modal-lg`}>
            <div className="modal-header">
                
            </div>
            <div className="modal-content">
            <div className="modal-body">
            <h1 className="modal-title text-center">{item?.title}</h1>
            <p className="modal-description">{item?.description}</p>
                </div>
                <div className="modal-footer flex justify-center gap-4">
                    <button className="bg-red-500 text-white px-4 py-2 rounded-md hover:bg-red-600 cursor-pointer" onClick={onDelete}>Delete</button>
                    <button className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 cursor-pointer" onClick={onHide}>Close</button>
                </div>
            </div>
        </div>
    );
}