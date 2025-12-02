"use client";

import { useState } from "react";
import { login } from "@/app/lib/data";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [msg, setMsg] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const result = await login(username, password);
    setMsg(JSON.stringify(result));
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        placeholder="username"
      />

      <input
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        type="password"
        placeholder="password"
      />

      <button type="submit">Sign In</button>

      <pre>{msg}</pre>
    </form>
  );
}
