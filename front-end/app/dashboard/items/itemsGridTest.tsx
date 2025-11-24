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
  
    const handleDeleteItem = () => {
  
    }

    const handleSaveItem = async (updatedItem: Partial<Item>) => {
        try {
            const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
            
            if (updatedItem.item_id) {
                // Update existing item - convert item_id to number for API
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
                        description: updatedItem.description,
                        category: updatedItem.category,
                        // Note: API doesn't support updating title, list_date, or creator_id in PUT endpoint
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
        setSelectedItem(null);
        setShowModal(true);
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