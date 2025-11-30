'use client';
import { useState, useEffect } from 'react';
import { Item } from '@/app/lib/definitions';  
import '@/app/dashboard/items/items.css';
interface ItemModalProps {
    show: boolean;
    onHide: () => void;
    item: Item | null;
    onDelete: () => void;
    onSave: (updatedItem: Partial<Item>) => void;
}

export default function ItemModal({ show, onHide, item, onDelete, onSave }: ItemModalProps) {
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [category, setCategory] = useState('');
    const [listDate, setListDate] = useState('');
    const [isOnEtsy, setIsOnEtsy] = useState(false);
    const [isOnEbay, setIsOnEbay] = useState(false);
    const [creatorId, setCreatorId] = useState('');
    const [price, setPrice] = useState(0);
    useEffect(() => {
        if (item) {
            setTitle(item.title || '');
            setDescription(item.description || '');
            setCategory(item.category || '');
            setListDate(item.list_date || '');
            setIsOnEtsy(item.isOnEtsy || false);
            setIsOnEbay(item.isOnEbay || false);
            setCreatorId(item.creator_id || '');
            setPrice(item.price || 0);
        }
    }, [item]);

    return (
        <div className={`modal ${show ? 'show' : ''} modal-dialog-centered modal-lg`}>
            <div className="modal-header">
                
            </div>
            <div className="modal-content">
            <div className="modal-body flex flex-col gap-4">
                <div className="flex flex-col gap-2">
                    <label htmlFor="title" className="font-semibold">Title</label>
                    <input
                        id="title"
                        type="text"
                        className="modal-title border border-gray-300 rounded-md px-3 py-2 w-full"
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                    />
                </div>
                <div className="flex flex-col gap-2">
                    <label htmlFor="description" className="font-semibold">Description</label>
                    <textarea
                        id="description"
                        className="modal-description border border-gray-300 rounded-md px-3 py-2 resize-none w-full"
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        rows={4}
                    />
                </div>
                <div className="flex flex-col gap-2">
                    <label htmlFor="price" className="font-semibold">Price</label>
                    <input
                        id="price"
                        type="number"
                        className="modal-price border border-gray-300 rounded-md px-3 py-2 w-full"
                        value={price?.toString() || ''}
                        onChange={(e) => setPrice(parseFloat(e.target.value))}
                    />
                </div>
                <div className="flex flex-col gap-2">
                    <label htmlFor="category" className="font-semibold">Category</label>
                    <input
                        id="category"
                        type="text"
                        className="modal-category border border-gray-300 rounded-md px-3 py-2 w-full"
                        value={category}
                        onChange={(e) => setCategory(e.target.value)}
                    />
                </div>
                <div className="flex flex-col gap-2">
                    <label htmlFor="list_date" className="font-semibold">List Date</label>
                    <input
                        id="list_date"
                        type="date"
                        className="modal-list-date border border-gray-300 rounded-md px-3 py-2 w-full"
                        value={listDate}
                        onChange={(e) => setListDate(e.target.value)}
                    />
                </div>
                <div className="flex items-center gap-2">
                    <input
                        id="isOnEtsy"
                        type="checkbox"
                        className="modal-isOnEtsy"
                        checked={isOnEtsy}
                        onChange={(e) => setIsOnEtsy(e.target.checked)}
                    />
                    <label htmlFor="isOnEtsy" className="font-semibold">Is On Etsy</label>
                </div>
                <div className="flex items-center gap-2">
                    <input
                        id="isOnEbay"
                        type="checkbox"
                        className="modal-isOnEbay"
                        checked={isOnEbay}
                        onChange={(e) => setIsOnEbay(e.target.checked)}
                    />
                    <label htmlFor="isOnEbay" className="font-semibold">Is On Ebay</label>
                </div>
                <div className="flex flex-col gap-2">
                    <label htmlFor="creator_id" className="font-semibold">Creator ID</label>
                    <input
                        id="creator_id"
                        type="text"
                        className="modal-creator-id border border-gray-300 rounded-md px-3 py-2 w-full"
                        value={creatorId}
                        onChange={(e) => setCreatorId(e.target.value)}
                    />
                </div>
            </div>
                <div className="modal-footer flex justify-center gap-4">
                    <button className="bg-green-500 text-white px-4 py-2 rounded-md hover:bg-green-600 cursor-pointer" onClick={() => onSave({
                        title,
                        description,
                        price,
                        category,
                        list_date: listDate,
                        isOnEtsy,
                        isOnEbay,
                        creator_id: creatorId,
                        item_id: item?.item_id || ''
                    })}>Save</button>
                    <button className="bg-red-500 text-white px-4 py-2 rounded-md hover:bg-red-600 cursor-pointer" onClick={onDelete}>Delete</button>
                    <button className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 cursor-pointer" onClick={onHide}>Close</button>
                </div>
            </div>
        </div>
    );
}