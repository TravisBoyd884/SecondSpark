import { cookies } from "next/headers";
import jwt from "jsonwebtoken";

interface JwtPayload {
  user_id: number;
  username: string;
  iat: number;
  exp: number;
}

export async function getCurrentUser(): Promise<JwtPayload | null> {
  const cookieStore = await cookies(); // <-- await this
  const token = cookieStore.get("auth_token")?.value;
  if (!token) return null;

  try {
    const secret = process.env.JWT_SECRET!;
    const decoded = jwt.verify(token, secret) as JwtPayload;
    return decoded;
  } catch (err) {
    return null;
  }
}
