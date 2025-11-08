import { useUser } from "../UserContext";
import type { User } from "../UserContext";
import { useEffect, useState, useCallback } from "react";
import { FaWallet, FaCopy, FaServer, FaPaperPlane } from "react-icons/fa";
import SendAcoin from "./SendAcoin";
import "../App.css";

interface Transaction {
  from: string;
  to: string;
  amount: number;
  timestamp: string;
  blockIndex: number;
}

function Wallet() {
  const { user, setUser } = useUser();
  const [balance, setBalance] = useState(user?.balance ?? 0);
  const [isMiner, setIsMiner] = useState(false);
  const [copied, setCopied] = useState(false);
  const [status, setStatus] = useState("");
  const [activeTab, setActiveTab] = useState("overview");
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [notifications, setNotifications] = useState<Array<{
    message: string;
    timestamp: string;
    read: boolean;
    type: 'sent' | 'received';
  }>>([]);

  const fetchTransactions = useCallback(async () => {
    if (user?.address) {
      try {
        const res = await fetch(`http://127.0.0.1:5000/api/transactions/${user.address}`);
        const data = await res.json();
        if (res.ok) {
          setTransactions(data.transactions);
          // Add new transaction notifications
          const recentTxs = data.transactions.filter((tx: Transaction) => 
            new Date(tx.timestamp).getTime() > new Date().getTime() - 300000 // Last 5 minutes
          );
          if (recentTxs.length > 0) {
            setNotifications(prev => [
              ...prev,
              ...recentTxs.map((tx: Transaction) => ({
                message: tx.to === user.address 
                  ? `Received ${tx.amount} AXC from ${tx.from.slice(0, 8)}...`
                  : `Sent ${tx.amount} AXC to ${tx.to.slice(0, 8)}...`,
                timestamp: tx.timestamp,
                read: false,
                type: tx.to === user.address ? 'received' : 'sent'
              }))
            ]);
          }
        }
      } catch (error) {
        console.error("Fetch transactions error:", error);
      }
    }
  }, [user?.address]);

  const fetchWalletData = useCallback(async () => {
    if (user?.address) {
      try {
        const res = await fetch(`http://127.0.0.1:5000/api/wallet/${user.address}`);
        const data = await res.json();
        if (res.ok) {
          setBalance(data.balance);
          setIsMiner(data.is_miner);
          setUser((prev: User | null) => prev ? { ...prev, balance: data.balance, isMiner: data.is_miner } : prev);
        } else {
          setStatus(data.error || "Failed to fetch wallet data");
        }
      } catch (error) {
        console.error("Fetch wallet data error:", error);
        setStatus("An error occurred while fetching wallet data.");
      }
    }
  }, [user?.address, setUser]);

  useEffect(() => {
    fetchWalletData();
    fetchTransactions();
    // Set up polling for new transactions
    const interval = setInterval(fetchTransactions, 10000); // Poll every 10 seconds
    return () => clearInterval(interval);
  }, [fetchWalletData, fetchTransactions]);

  const handleCopy = () => {
    if (user?.address) {
      navigator.clipboard.writeText(user.address);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    }
  };

  const registerAsMiner = async () => {
    if (!user) return;
    setStatus("Registering...");
    try {
      const res = await fetch("http://127.0.0.1:5000/api/register-miner", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ address: user.address }),
      });
      const data = await res.json();
      if (res.ok) {
        setStatus("Successfully registered as a miner!");
        // Refresh wallet data to show new status
        fetchWalletData();
      } else {
        setStatus(data.error || "Failed to register as miner");
      }
    } catch (error) {
        console.error("Miner registration error:", error);
        setStatus("An error occurred during miner registration.");
    }
  };

  if (!user) {
    return (
      <div className="container py-5">
        <div className="alert alert-warning fw-bold text-center">
          Please log in to view your wallet.
        </div>
      </div>
    );
  }

  return (
    <div className="container wallet-container">
      <div className="card shadow wallet-card">
        <h2 className="wallet-title">
          <FaWallet className="me-2 text-white" /> Wallet
        </h2>
        
        <div className="nav nav-tabs mb-4">
          <button 
            className={`nav-link ${activeTab === "overview" ? "active" : ""}`} 
            onClick={() => setActiveTab("overview")}
          >
            <FaWallet className="me-2" /> Overview
          </button>
          <button 
            className={`nav-link ${activeTab === "send" ? "active" : ""}`} 
            onClick={() => setActiveTab("send")}
          >
            <FaPaperPlane className="me-2" /> Send
          </button>
        </div>

        {activeTab === "overview" ? (
          <>
            <div className="wallet-info">
              Address: {user.address.slice(0, 8) + "..." + user.address.slice(-4)}
              <span className="ms-2" style={{ cursor: "pointer" }} onClick={handleCopy}>
                <FaCopy className="text-info" />
              </span>
              {copied && <span className="text-success fw-bold ms-2">Copied!</span>}
            </div>
            <div className="wallet-info">
              Username: {user.username}
            </div>
            <div className="wallet-info">
              Balance: <span className="wallet-balance">{balance.toFixed(4)}</span> AXC
            </div>
            <div className="wallet-info">
              Miner Status: 
              {isMiner ? 
                <span className="badge bg-success ms-2">Active Miner</span> : 
                <span className="badge bg-secondary ms-2">Not a Miner</span>
              }
            </div>
            {notifications.length > 0 && (
              <div className="mt-3">
                <h5 className="text-white mb-2">Recent Notifications</h5>
                <div className="notification-list">
                  {notifications.map((notif, index) => (
                    <div 
                      key={index} 
                      className={`alert ${notif.read ? 'alert-secondary' : 
                        notif.type === 'received' ? 'alert-success' : 'alert-primary'} mb-2`}
                    >
                      <div className="d-flex justify-content-between align-items-start">
                        <div>
                          <span className={`badge ${notif.type === 'received' ? 'bg-success' : 'bg-primary'} me-2`}>
                            {notif.type === 'received' ? 'Received' : 'Sent'}
                          </span>
                          {notif.message}
                        </div>
                        <small className="text-muted">
                          {new Date(notif.timestamp).toLocaleString()}
                        </small>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            {!isMiner && (
              <div className="mt-4">
                <button className="btn btn-primary fw-bold w-100" onClick={registerAsMiner}>
                  <FaServer className="me-2" />Register as a Miner
                </button>
                <div className="form-text text-light mt-2">Become a miner to help secure the network and earn gas fees from transactions. (Requires a small gas fee).</div>
              </div>
            )}
            {status && <div className={`alert mt-3 ${status.startsWith("Successfully") ? 'alert-success' : 'alert-danger'}`}>{status}</div>}
            
            <div className="mt-4">
              <h5 className="text-white mb-3">Transaction History</h5>
              <div className="transaction-list" style={{ maxHeight: '300px', overflowY: 'auto' }}>
                {transactions.map((tx, index) => (
                  <div key={index} className="card bg-dark mb-2 p-3">
                    <div className="d-flex justify-content-between align-items-start">
                      <div>
                        {tx.to === user.address ? (
                          <span className="badge bg-success me-2">Received</span>
                        ) : (
                          <span className="badge bg-primary me-2">Sent</span>
                        )}
                        <span className="text-white">
                          {tx.amount.toFixed(4)} AXC
                        </span>
                      </div>
                      <small className="text-muted">
                        {new Date(tx.timestamp).toLocaleString()}
                      </small>
                    </div>
                    <div className="mt-2">
                      <small className="text-muted">
                        {tx.to === user.address ? 'From: ' : 'To: '}
                        {tx.to === user.address ? tx.from : tx.to}
                      </small>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </>
        ) : (
          <SendAcoin onSuccess={fetchWalletData} />
        )}
      </div>
    </div>
  );
}

export default Wallet;
