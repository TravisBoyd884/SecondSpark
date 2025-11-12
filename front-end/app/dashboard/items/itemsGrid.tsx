"use client";
import { Item } from "@/app/lib/definitions";
import Card from 'react-bootstrap/Card'
import Button from 'react-bootstrap/Button'
import ItemModal from "./itemModal";
import { useEffect, useState } from "react";
import { item } from "@/app/lib/placeholder-data";
import "@/app/dashboard/items/items.css";

export default function ItemsGrid() {
  const [items, setItems] = useState<Item[]>([]);
  const [showModal, setShowModal] = useState(false);
  const [selectedItem, setSelectedItem] = useState<Item | null>(null);

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

    
    return (
        <div className="bootstrap-scope">
        <ItemModal show={showModal} onHide={handleCloseModal} item={selectedItem} onDelete={handleDeleteItem} />
    <div className="d-flex flex-wrap gap-4">
    
    {items.map((item) => (
      <Card key={item.item_id}>
        {/* <Card.Img variant="top" src="holder.js/100px180" /> */}
        <Card.Body>
          <Card.Title>{item.title}</Card.Title>
          <Card.Text>{item.description}</Card.Text>
          <Button variant="primary" onClick={() => handleViewItem(item)}>View</Button>
          <Button variant="danger" onClick={() => handleDeleteItem()}>Delete</Button>
        </Card.Body>
      </Card>
    ))}
    </div>
    </div>
    );
}