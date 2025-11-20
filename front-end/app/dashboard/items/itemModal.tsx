'use client';
import { Item } from '@/app/lib/definitions';  
import '@/app/dashboard/items/items.css';
interface ItemModalProps {
    show: boolean;
    onHide: () => void;
    item: Item | null;
    onDelete: () => void;
    onSave: () => void;
}

export default function ItemModal({ show, onHide, item, onDelete, onSave }: ItemModalProps) {
    return (
        <div className={`modal ${show ? 'show' : ''} modal-dialog-centered modal-lg`}>
            <div className="modal-header">
                
            </div>
            <div className="modal-content">
            <div className="modal-body flex flex-col gap-4">
                <h1 className="modal-title text-center">{item?.title}</h1>
                <p className="modal-description">{item?.description}</p>
                <div className="modal-category">Category: {item?.category}</div>
                <p className="modal-list-date">List Date: {item?.list_date}</p>
                <p className="modal-isOnEtsy">Is On Etsy: {item?.isOnEtsy ? 'Yes' : 'No'}</p>
                <p className="modal-isOnEbay">Is On Ebay: {item?.isOnEbay ? 'Yes' : 'No'}</p>
                <p className="modal-creator-id">Creator ID: {item?.creator_id}</p>
            </div>
                <div className="modal-footer flex justify-center gap-4">
                    <button className="bg-green-500 text-white px-4 py-2 rounded-md hover:bg-green-600 cursor-pointer" onClick={onSave}>Save</button>
                    <button className="bg-red-500 text-white px-4 py-2 rounded-md hover:bg-red-600 cursor-pointer" onClick={onDelete}>Delete</button>
                    <button className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 cursor-pointer" onClick={onHide}>Close</button>
                </div>
            </div>
        </div>
    );
}