// app/dashboard/items/itemsGridTest.tsx
"use client";

import { useState, useEffect } from "react";
import { Item } from "@/app/lib/definitions";
import ItemModal from "./itemModal";
import "@/app/dashboard/items/items.css";

interface ItemImage {
  image_id: number;
  item_id: number;
  image_url: string;
  is_primary: boolean;
}

interface ItemsGridTestProps {
  userId: number;
  isAdmin: boolean;
}

export default function ItemsGridTest({ userId, isAdmin }: ItemsGridTestProps) {
  const [items, setItems] = useState<Item[]>([]);
  const [selectedItem, setSelectedItem] = useState<Item | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [search, setSearch] = useState("");
  const [itemImages, setItemImages] = useState<Record<string, string>>({});

  useEffect(() => {
    refreshItems();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId]);

  const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";

  const refreshItems = async () => {
    try {
      // Get items for the LOGGED-IN USER
      const response = await fetch(`${apiBaseUrl}/users/${userId}/items`);

      if (!response.ok) {
        console.error("Failed to fetch user items");
        return;
      }

      const fetchedItems = await response.json();

      const itemsWithDefaults: Item[] = fetchedItems.map((item: any) => ({
        item_id: String(item.item_id),
        title: item.title || "",
        description: item.description || "",
        category: item.category || "",
        list_date: item.list_date || "",
        price: item.price || 0,
        isOnEtsy: item.isOnEtsy || false,
        isOnEbay: item.isOnEbay || false,
        // IMPORTANT: creator_id from backend, fallback to logged-in user
        creator_id: String(item.creator_id ?? userId),
      }));

      setItems(itemsWithDefaults);

      await fetchImagesForItems(itemsWithDefaults);
    } catch (error) {
      console.error("Error fetching items:", error);
    }
  };

  const fetchImagesForItems = async (itemsList: Item[]) => {
    const imagesMap: Record<string, string> = {};

    await Promise.all(
      itemsList.map(async (item) => {
        try {
          const itemIdNum = parseInt(item.item_id, 10);
          if (isNaN(itemIdNum)) return;

          const response = await fetch(
            `${apiBaseUrl}/item/${itemIdNum}/images`,
          );
          if (!response.ok) return;

          const data = await response.json();
          let images: ItemImage[] = [];

          if (Array.isArray(data)) {
            images = data;
          } else if (data.images && Array.isArray(data.images)) {
            images = data.images;
          }

          if (images && images.length > 0) {
            const imageUrl = images[0].image_url;
            imagesMap[item.item_id] = `${apiBaseUrl}${imageUrl}`;
          }
        } catch (error) {
          console.error(
            `Error fetching images for item ${item.item_id}:`,
            error,
          );
        }
      }),
    );

    setItemImages(imagesMap);
  };

  const handleViewItem = (item: Item) => {
    setSelectedItem(item);
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setSelectedItem(null);
  };

  const handleDeleteItem = async (item?: Item) => {
    const itemToDelete = item || selectedItem;

    if (!itemToDelete?.item_id) {
      console.error("No item selected for deletion");
      return;
    }

    const response = await fetch(
      `${apiBaseUrl}/items/${itemToDelete.item_id}`,
      {
        method: "DELETE",
      },
    );
    if (!response.ok) {
      console.error("Failed to delete item");
      return;
    }

    await refreshItems();
    setShowModal(false);
    setSelectedItem(null);
  };

  const syncItemToEbay = async (item: Partial<Item>, itemId?: string) => {
    try {
      const sku = itemId || item.item_id || `ITEM-${Date.now()}`;

      const ebayPayload = {
        item_id: itemId || item.item_id || null,
        title: item.title || "",
        description: item.description || "",
        category: item.category || "",
        quantity: 1,
        price: item.price || 0,
      };

      const response = await fetch(`${apiBaseUrl}/ebay/inventory/${sku}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(ebayPayload),
      });

      if (!response.ok) {
        const error = await response.json();
        console.error("Failed to sync item to eBay:", error);
        alert(
          `Item saved, but failed to sync to eBay: ${
            error.error || error.details || "Unknown error"
          }`,
        );
        return false;
      }

      const ebayResult = await response.json();
      console.log("Item synced to eBay successfully:", ebayResult);
      return true;
    } catch (error) {
      console.error("Error syncing item to eBay:", error);
      alert("Item saved, but an error occurred while syncing to eBay");
      return false;
    }
  };

  const handleSaveItem = async (updatedItem: Partial<Item>) => {
    try {
      let savedItemId: string | undefined;

      if (updatedItem.item_id) {
        // UPDATE existing
        const itemId = parseInt(updatedItem.item_id, 10);
        if (isNaN(itemId)) {
          alert("Invalid item ID");
          return;
        }

        const response = await fetch(`${apiBaseUrl}/items/${itemId}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            title: updatedItem.title,
            description: updatedItem.description,
            category: updatedItem.category,
            list_date: updatedItem.list_date,
            price: updatedItem.price,
          }),
        });

        if (!response.ok) {
          const error = await response.json();
          console.error("Failed to update item:", error);
          alert(`Failed to update item: ${error.error || "Unknown error"}`);
          return;
        }

        const savedItem = await response.json();
        console.log("Item updated successfully:", savedItem);
        savedItemId = String(savedItem.item_id);
      } else {
        // CREATE new - check authorization
        if (!isAdmin) {
          alert("Only administrators can create items");
          return;
        }

        if (!updatedItem.title) {
          alert("Title is required to create a new item");
          return;
        }

        const response = await fetch(`${apiBaseUrl}/items`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            title: updatedItem.title,
            description: updatedItem.description,
            category: updatedItem.category,
            list_date: updatedItem.list_date,
            price: updatedItem.price,
            // <-- USE LOGGED-IN USER AS CREATOR
            creator_id: userId,
          }),
        });

        if (!response.ok) {
          const error = await response.json();
          console.error("Failed to create item:", error);
          alert(`Failed to create item: ${error.error || "Unknown error"}`);
          return;
        }

        const savedItem = await response.json();
        console.log("Item created successfully:", savedItem);
        savedItemId = String(savedItem.item_id);
      }

      if (updatedItem.isOnEbay) {
        await syncItemToEbay(updatedItem, savedItemId);
      }

      await refreshItems();
      setShowModal(false);
      setSelectedItem(null);
    } catch (error) {
      console.error("Error saving item:", error);
      alert("An error occurred while saving the item");
    }
  };

  const handleCreateItem = async () => {
    setSelectedItem({
      item_id: "",
      title: "",
      description: "",
      category: "",
      list_date: "",
      price: 0,
      isOnEtsy: false,
      isOnEbay: false,
      // Pre-fill with logged-in user; modal doesn’t need to expose it
      creator_id: String(userId),
    });
    setShowModal(true);
  };

  const handleSearch = async () => {
    try {
      const itemId = parseInt(search.trim(), 10);
      if (isNaN(itemId)) {
        alert("Please enter a valid item ID (number)");
        return;
      }

      const response = await fetch(`${apiBaseUrl}/items/${itemId}`);

      if (!response.ok) {
        if (response.status === 404) {
          alert(`Item with ID ${itemId} not found`);
          setItems([]);
          setItemImages({});
        } else {
          console.error("Failed to search item");
          alert("Failed to search item");
        }
        return;
      }

      const fetchedItem = await response.json();

      // Optional: you could check fetchedItem.creator_id === userId
      const itemsWithDefaults: Item[] = [
        {
          item_id: String(fetchedItem.item_id),
          title: fetchedItem.title || "",
          description: fetchedItem.description || "",
          category: fetchedItem.category || "",
          list_date: fetchedItem.list_date || "",
          price: fetchedItem.price || 0,
          isOnEtsy: fetchedItem.isOnEtsy || false,
          isOnEbay: fetchedItem.isOnEbay || false,
          creator_id: String(fetchedItem.creator_id ?? userId),
        },
      ];

      setItems(itemsWithDefaults);
      await fetchImagesForItems(itemsWithDefaults);
    } catch (error) {
      console.error("Error searching items:", error);
      alert("An error occurred while searching for the item");
    }
  };

  return (
    <div>
      {isAdmin && (
        <div className="flex justify-center mb-4">
          <button
            className="bg-black text-white w-8/10 ml-4 mr-4 my-4 px-4 py-2 rounded-md hover:bg-gray-600 cursor-pointer"
            onClick={handleCreateItem}
          >
            Create Item
          </button>
        </div>
      )}
      <div className="flex justify-center mb-4">
        <button
          className="bg-black text-white w-1/10 px-4 py-2 rounded-md hover:bg-gray-600 cursor-pointer mb-4 ml-4 mr-4"
          onClick={handleSearch}
        >
          Search
        </button>
        <input
          type="text"
          className="border border-gray-300 w-8/10 rounded-md px-3 py-2 mb-4 ml-4 mr-4 w-4/5"
          placeholder="Search by Item ID"
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      <ItemModal
        show={showModal}
        onHide={handleCloseModal}
        item={selectedItem}
        onDelete={handleDeleteItem}
        onSave={handleSaveItem}
      />

      <div className="grid grid-cols-3 gap-4 mt-4 mb-4">
        {items.map((item) => (
          <div
            className="card p-4 shadow-sm rounded-md h-full flex flex-col"
            key={item.item_id}
          >
            {itemImages[item.item_id] && (
              <img
                src={itemImages[item.item_id]}
                alt={item.title}
                className="w-full h-48 object-cover rounded-md mb-4"
                onError={(e) => {
                  (e.target as HTMLImageElement).style.display = "none";
                }}
              />
            )}
            <h2 className="text-lg font-bold mb-2">{item.title}</h2>
            <p className="flex-grow mb-4">{item.description}</p>
            <div className="flex gap-4 mt-auto">
              <button
                className="bg-white text-black border border-black px-4 py-2 rounded-md hover:bg-gray-100 cursor-pointer"
                onClick={() => handleViewItem(item)}
              >
                View
              </button>
              <button
                className="bg-black text-white px-4 py-2 rounded-md hover:bg-gray-800 cursor-pointer"
                onClick={() => handleDeleteItem(item)}
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

