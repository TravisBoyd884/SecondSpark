// This file contains placeholder data that you'll be replacing with real data in the Data Fetching chapter:
// https://nextjs.org/learn/dashboard-app/fetching-data
const users = [
  {
    user_id: "410544b2-4001-4271-9855-fec4b6a6442a",
    username: "User",
    password: "123456",
    email: "user@nextmail.com",
    organization_id: "42ae82f2-7f68-4c7c-a27a-ba000a207a10",
    securityQuestion: "What is the name of your first pet?",
    organization_role: "Admin",
  },
];

const organizations = [
  {
    organization_id: "42ae82f2-7f68-4c7c-a27a-ba000a207a10",
    name: "Gibson Refurbishing",
  },
];

const item = [
  {
    item_id: "f6b2ef52-296d-4729-9aaa-86337e85a0aa",
    title: 'HP Victus 15.6\" Gaming Laptop',
    description:
      "15.6 inch FHD 144Hz IPS Windows Gaming Laptop Intel Core i5-13420H 16GB RAM 512GB SSD RTX 4050 Mica Silver",
    category: "Tech",
    list_date: "2025-11-06",
    isOnEtsy: false,
    isOnEbay: false,
    creator_id: "410544b2-4001-4271-9855-fec4b6a6442a",
  },
];

const resellers = [
  {
    reseller_id: "f789b1a4-9a22-44ea-b9f6-cb98cd9ca37f",
    reseller_name: "Ebay",
  },
  {
    reseller_id: "a79d7dcf-161b-4b97-ad54-a342a6aad087",
    reseller_name: "Etsey",
  },
];

const transactions = [
  {
    transaction_id: "86681f54-3dd9-4ad2-b818-908e97d0ba0d",
    sale_date: "2025-11-06",
    total: 599.0,
    tax: 35.94,
    reseller_commission: 41.93,
    reseller_id: "f789b1a4-9a22-44ea-b9f6-cb98cd9ca37f",
  },
];

const transaction_items = [
  {
    transaction_item_id: "28f143d0-17ec-44f7-a4b2-94cbddd38afc",
    item_id: "f6b2ef52-296d-4729-9aaa-86337e85a0aa",
    transaction_id: "86681f54-3dd9-4ad2-b818-908e97d0ba0d",
  },
];

const customers = [
  {
    id: "d6e15727-9fe1-4961-8c5b-ea44a9bd81aa",
    name: "Evil Rabbit",
    email: "evil@rabbit.com",
    image_url: "/customers/evil-rabbit.png",
  },
  {
    id: "3958dc9e-712f-4377-85e9-fec4b6a6442a",
    name: "Delba de Oliveira",
    email: "delba@oliveira.com",
    image_url: "/customers/delba-de-oliveira.png",
  },
  {
    id: "3958dc9e-742f-4377-85e9-fec4b6a6442a",
    name: "Lee Robinson",
    email: "lee@robinson.com",
    image_url: "/customers/lee-robinson.png",
  },
  {
    id: "76d65c26-f784-44a2-ac19-586678f7c2f2",
    name: "Michael Novotny",
    email: "michael@novotny.com",
    image_url: "/customers/michael-novotny.png",
  },
  {
    id: "CC27C14A-0ACF-4F4A-A6C9-D45682C144B9",
    name: "Amy Burns",
    email: "amy@burns.com",
    image_url: "/customers/amy-burns.png",
  },
  {
    id: "13D07535-C59E-4157-A011-F8D2EF4E0CBB",
    name: "Balazs Orban",
    email: "balazs@orban.com",
    image_url: "/customers/balazs-orban.png",
  },
];

const invoices = [
  {
    customer_id: customers[0].id,
    amount: 15795,
    status: "pending",
    date: "2022-12-06",
  },
  {
    customer_id: customers[1].id,
    amount: 20348,
    status: "pending",
    date: "2022-11-14",
  },
  {
    customer_id: customers[4].id,
    amount: 3040,
    status: "paid",
    date: "2022-10-29",
  },
  {
    customer_id: customers[3].id,
    amount: 44800,
    status: "paid",
    date: "2023-09-10",
  },
  {
    customer_id: customers[5].id,
    amount: 34577,
    status: "pending",
    date: "2023-08-05",
  },
  {
    customer_id: customers[2].id,
    amount: 54246,
    status: "pending",
    date: "2023-07-16",
  },
  {
    customer_id: customers[0].id,
    amount: 666,
    status: "pending",
    date: "2023-06-27",
  },
  {
    customer_id: customers[3].id,
    amount: 32545,
    status: "paid",
    date: "2023-06-09",
  },
  {
    customer_id: customers[4].id,
    amount: 1250,
    status: "paid",
    date: "2023-06-17",
  },
  {
    customer_id: customers[5].id,
    amount: 8546,
    status: "paid",
    date: "2023-06-07",
  },
  {
    customer_id: customers[1].id,
    amount: 500,
    status: "paid",
    date: "2023-08-19",
  },
  {
    customer_id: customers[5].id,
    amount: 8945,
    status: "paid",
    date: "2023-06-03",
  },
  {
    customer_id: customers[2].id,
    amount: 1000,
    status: "paid",
    date: "2022-06-05",
  },
];

const revenue = [
  { month: "Jan", revenue: 2000 },
  { month: "Feb", revenue: 1800 },
  { month: "Mar", revenue: 2200 },
  { month: "Apr", revenue: 2500 },
  { month: "May", revenue: 2300 },
  { month: "Jun", revenue: 3200 },
  { month: "Jul", revenue: 3500 },
  { month: "Aug", revenue: 3700 },
  { month: "Sep", revenue: 2500 },
  { month: "Oct", revenue: 2800 },
  { month: "Nov", revenue: 3000 },
  { month: "Dec", revenue: 4800 },
];

export {
  users,
  customers,
  invoices,
  revenue,
  organizations,
  item,
  resellers,
  transactions,
  transaction_items,
};
