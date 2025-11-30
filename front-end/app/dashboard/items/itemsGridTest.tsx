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
    const [search, setSearch] = useState('');
    useEffect(() => {
        setItems(item);
        refreshItems();
    }, []);

    const refreshItems = async () => {
        try {
            const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
            const response = await fetch(`${apiBaseUrl}/items`);
            
            if (!response.ok) {
                console.error('Failed to fetch items');
                return;
            }

            const fetchedItems = await response.json();
            // Map API response to Item type, converting types and adding defaults
            const itemsWithDefaults: Item[] = fetchedItems.map((item: any) => ({
                item_id: String(item.item_id),
                title: item.title || '',
                description: item.description || '',
                category: item.category || '',
                list_date: item.list_date || '',
                price: item.price || 0,
                isOnEtsy: item.isOnEtsy || false,
                isOnEbay: item.isOnEbay || false,
                creator_id: String(item.creator_id || ''),
            }));
            setItems(itemsWithDefaults);
        } catch (error) {
            console.error('Error fetching items:', error);
        }
    }
  
    const handleViewItem = (item: Item) => {
      setSelectedItem(item);
      setShowModal(true);
    }
  
    const handleCloseModal = () => {
      setShowModal(false);
      setSelectedItem(null);
    }
  
    const handleDeleteItem = async () => {
        console.log('Delete item');
        console.log(selectedItem);
        const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

        const response = await fetch(`${apiBaseUrl}/items/${selectedItem?.item_id}`, {
            method: 'DELETE',
        });
        if (!response.ok) {
            console.error('Failed to delete item');
            return;
        }
        const data = await response.json();
        console.log(data);
        await refreshItems();
        setShowModal(false);
        setSelectedItem(null);
    }

    const handleSaveItem = async (updatedItem: Partial<Item>) => {
        try {
            const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
            
            if (updatedItem.item_id) {
                const itemId = parseInt(updatedItem.item_id, 10);
                if (isNaN(itemId)) {
                    alert('Invalid item ID');
                    return;
                }

                const response = await fetch(`${apiBaseUrl}/items/${itemId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        title: updatedItem.title,
                        description: updatedItem.description,
                        category: updatedItem.category,
                        list_date: updatedItem.list_date,
                    }),
                });

                if (!response.ok) {
                    const error = await response.json();
                    console.error('Failed to update item:', error);
                    alert(`Failed to update item: ${error.error || 'Unknown error'}`);
                    return;
                }

                const savedItem = await response.json();
                console.log('Item updated successfully:', savedItem);
            } else {
                // Create new item
                if (!updatedItem.title || !updatedItem.creator_id) {
                    alert('Title and Creator ID are required to create a new item');
                    return;
                }

                // Convert creator_id to number for API (API expects INT)
                const creatorId = parseInt(updatedItem.creator_id, 10);
                if (isNaN(creatorId)) {
                    alert('Creator ID must be a valid number');
                    return;
                }

                const response = await fetch(`${apiBaseUrl}/items`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        title: updatedItem.title,
                        description: updatedItem.description,
                        category: updatedItem.category,
                        list_date: updatedItem.list_date,
                        creator_id: creatorId,
                    }),
                });

                if (!response.ok) {
                    const error = await response.json();
                    console.error('Failed to create item:', error);
                    alert(`Failed to create item: ${error.error || 'Unknown error'}`);
                    return;
                }

                const savedItem = await response.json();
                console.log('Item created successfully:', savedItem);
            }

            // Refresh items list
            await refreshItems();
            // Close modal
            setShowModal(false);
            setSelectedItem(null);
        } catch (error) {
            console.error('Error saving item:', error);
            alert('An error occurred while saving the item');
        }
    }

    const handleCreateItem = async () => {
        setSelectedItem({
            item_id: '',
            title: '',
            description: '',
            category: '',
            list_date: '',
            price: 0,
            isOnEtsy: false,
            isOnEbay: false,
            creator_id: '',
        });
        setShowModal(true);
    }

    return (
        <div>
            <button className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 cursor-pointer mb-4 ml-4 mr-4" onClick={handleCreateItem}>Create Item</button>
            <input type="text" className="border border-gray-300 rounded-md px-3 py-2 mb-4 ml-4 mr-4 w-4/5" placeholder="Search items" onChange={(e) => setSearch(e.target.value)} />
            <ItemModal show={showModal} onHide={handleCloseModal} item={selectedItem} onDelete={handleDeleteItem} onSave={handleSaveItem} />
            <div className="grid grid-cols-3 gap-4 mt-4 mb-4">
                
                
                {items.map((item) => (
                    <div className="card p-4 shadow-sm rounded-md h-full flex flex-col" key={item.item_id}>
                        <h2 className="text-lg font-bold mb-2">{item.title}</h2>
                        <p className="flex-grow mb-4">{item.description}</p>
                        <div className="flex gap-4 mt-auto">
                            <button className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 cursor-pointer" onClick={() => handleViewItem(item)}>View</button>
                            <button className="bg-red-500 text-white px-4 py-2 rounded-md hover:bg-red-600 cursor-pointer" onClick={() => handleDeleteItem()}>Delete</button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}