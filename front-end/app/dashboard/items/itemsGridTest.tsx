'use client';
import { useState, useEffect } from 'react';
import { Item } from '@/app/lib/definitions';
import { item } from '@/app/lib/placeholder-data';
import ItemModal from './itemModal';
import '@/app/dashboard/items/items.css';

export default function ItemsGridTest() {
    const [items, setItems] = useState<Item[]>([]);
    const [selectedItem, setSelectedItem] = useState<Item | null>(null);
    const [showModal, setShowModal] = useState(false);

    useEffect(() => {
        setItems(item);
        refreshItems();
    }, []);

    const refreshItems = async () => {

    }
  
    const handleViewItem = (item: Item) => {
      setSelectedItem(item);
      setShowModal(true);
    }
  
    const handleCloseModal = () => {
      setShowModal(false);
    }
  
    const handleDeleteItem = () => {
  
    }

    const handleSaveItem = () => {
  
    }

    return (
        <div>
            <div className="flex flex-wrap justify-content-center gap-4 mt-4 mb-4">
                <ItemModal show={showModal} onHide={handleCloseModal} item={selectedItem} onDelete={handleDeleteItem} onSave={handleSaveItem} />
                {items.map((item) => (
                    <div className="card p-4 shadow-sm rounded-md" key={item.item_id}>
                        <h2 className="text-lg font-bold">{item.title}</h2>
                        <p>{item.description}</p>
                        <div className="flex gap-4">
                            <button className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 cursor-pointer" onClick={() => handleViewItem(item)}>View</button>
                            <button className="bg-red-500 text-white px-4 py-2 rounded-md hover:bg-red-600 cursor-pointer" onClick={() => handleDeleteItem()}>Delete</button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}