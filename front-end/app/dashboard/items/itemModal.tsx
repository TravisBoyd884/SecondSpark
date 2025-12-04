'use client';
import { useState, useEffect } from 'react';
import { Item } from '@/app/lib/definitions';  
import '@/app/dashboard/items/items.css';

interface ItemImage {
    image_id: number;
    item_id: number;
    image_url: string;
    is_primary: boolean;
}

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
    const [images, setImages] = useState<ItemImage[]>([]);
    const [uploading, setUploading] = useState(false);
    const [selectedFile, setSelectedFile] = useState<File | null>(null);

    const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

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
            
            // Fetch images if item has an ID
            if (item.item_id) {
                fetchImages(item.item_id);
            } else {
                setImages([]);
            }
        } else {
            setImages([]);
        }
    }, [item]);

    const fetchImages = async (itemId: string) => {
        try {
            const itemIdNum = parseInt(itemId, 10);
            if (isNaN(itemIdNum)) {
                return;
            }
            
            const response = await fetch(`${apiBaseUrl}/item/${itemIdNum}/images`);
            if (response.ok) {
                const data = await response.json();
                // Handle both array and object responses
                if (Array.isArray(data)) {
                    setImages(data);
                } else if (data.images) {
                    setImages(data.images);
                } else {
                    setImages([]);
                }
            } else if (response.status === 404) {
                // No images found is not an error
                setImages([]);
            } else {
                console.error('Failed to fetch images');
                setImages([]);
            }
        } catch (error) {
            console.error('Error fetching images:', error);
            setImages([]);
        }
    };

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setSelectedFile(e.target.files[0]);
        }
    };

    const handleUploadImage = async () => {
        if (!selectedFile || !item?.item_id) {
            alert('Please select a file and ensure the item is saved first');
            return;
        }

        const itemIdNum = parseInt(item.item_id, 10);
        if (isNaN(itemIdNum)) {
            alert('Invalid item ID');
            return;
        }

        setUploading(true);
        try {
            const formData = new FormData();
            formData.append('file', selectedFile);
            formData.append('is_primary', images.length === 0 ? 'true' : 'false');

            const response = await fetch(`${apiBaseUrl}/item/${itemIdNum}/image`, {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                const error = await response.json();
                alert(`Failed to upload image: ${error.error || 'Unknown error'}`);
                return;
            }

            const result = await response.json();
            console.log('Image uploaded successfully:', result);
            
            // Refresh images list
            await fetchImages(item.item_id);
            setSelectedFile(null);
            
            // Reset file input
            const fileInput = document.getElementById('image-upload') as HTMLInputElement;
            if (fileInput) {
                fileInput.value = '';
            }
        } catch (error) {
            console.error('Error uploading image:', error);
            alert('An error occurred while uploading the image');
        } finally {
            setUploading(false);
        }
    };

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
                
                {/* Image Upload Section */}
                {item?.item_id && (
                    <div className="flex flex-col gap-2 border-t pt-4 mt-4">
                        <label className="font-semibold">Images</label>
                        
                        {/* Image Upload Input */}
                        <div className="flex flex-col gap-2">
                            <input
                                id="image-upload"
                                type="file"
                                accept="image/png,image/jpeg,image/jpg,image/gif"
                                onChange={handleFileSelect}
                                className="border border-gray-300 rounded-md px-3 py-2 w-full"
                            />
                            {selectedFile && (
                                <button
                                    onClick={handleUploadImage}
                                    disabled={uploading}
                                    className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 cursor-pointer disabled:bg-gray-400 disabled:cursor-not-allowed"
                                >
                                    {uploading ? 'Uploading...' : 'Upload Image'}
                                </button>
                            )}
                        </div>
                        
                        {/* Display Existing Images */}
                        {images.length > 0 && (
                            <div className="mt-4">
                                <div className="grid grid-cols-3 gap-4">
                                    {images.map((image) => (
                                        <div key={image.image_id} className="relative">
                                            <img
                                                src={`${apiBaseUrl}${image.image_url}`}
                                                alt={`Item ${item.item_id} image ${image.image_id}`}
                                                className="w-full h-32 object-cover rounded-md border border-gray-300"
                                            />
                                            {image.is_primary && (
                                                <span className="absolute top-1 left-1 bg-green-500 text-white text-xs px-2 py-1 rounded">
                                                    Primary
                                                </span>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                )}
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