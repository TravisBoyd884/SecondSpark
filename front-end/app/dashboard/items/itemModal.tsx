import Modal from 'react-bootstrap/Modal'
import Button from 'react-bootstrap/Button'
import { Item } from '@/app/lib/definitions';  

interface ItemModalProps {
    show: boolean;
    onHide: () => void;
    item: Item | null;
    onDelete: () => void;
}

export default function ItemModal({ show, onHide, item }: ItemModalProps) {
    return (
        <Modal show={show} onHide={onHide}>
            <Modal.Header closeButton>
                <Modal.Title>{item?.title}</Modal.Title>
            </Modal.Header>
        </Modal>
    );
}