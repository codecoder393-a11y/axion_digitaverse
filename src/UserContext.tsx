import { createContext, useContext, useState } from "react";

export interface User {
  address: string;
  username: string;
  balance: number;
  profilePic: string;
  isMiner: boolean;
  token: string;
}

const UserContext = createContext<any>(null);

export function UserProvider({ children }: any) {
  const [user, setUser] = useState<any>(null);
  return (
    <UserContext.Provider value={{ user, setUser }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  return useContext(UserContext);
}