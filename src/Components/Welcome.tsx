
import { useUser } from "../UserContext";
import { FaCopy } from "react-icons/fa";
import { QRCodeCanvas } from "qrcode.react";
import { useState, useRef } from "react";
import "../App.css";

function shortAddress(address: string) {
  if (!address) return "";
  return address.slice(0, 8) + "..." + address.slice(-4);
}

function WelcomePage() {
  const { user, setUser } = useUser();
  const [copied, setCopied] = useState(false);
  const [showPopup, setShowPopup] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleCopy = () => {
    if (user?.address) {
      navigator.clipboard.writeText(user.address);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    }
  };

  const handleUpload = async () => {
    if (!user || !fileInputRef.current?.files?.[0]) return;
    const formData = new FormData();
    formData.append("address", user.address);
    formData.append("profilePic", fileInputRef.current.files[0]);
    const res = await fetch("http://127.0.0.1:5000/api/upload-profile-pic", {
      method: "POST",
      body: formData,
    });
    if (res.ok) {
      const data = await res.json();
      // Update user context with new profilePic
      setUser({ ...user, profilePic: data.profilePic });
      setShowPopup(false);
    }
  };

  const profilePicUrl = user?.profilePic
    ? `http://127.0.0.1:5000/api/profile-pic/${user.address}?t=${Date.now()}`
    : "/default-profile.png";

  return (
    <div className="welcome-container">
      
      <div className="card shadow welcome-card">
        <h1 className="welcome-title">
          Enjoy Your Web 3.0 with Axion Digitaverse Infrastructure
        </h1>
        <p className="welcome-subtitle">
          Welcome to the future of decentralized finance, identity, and smart contracts.
        </p>
        {user && (
          <div className="text-center mt-3">
            <img
              src={profilePicUrl}
              alt="Profile"
              className="profile-pic"
              onClick={() => setShowPopup(true)}
            />
            <h5 className="welcome-username">
              Welcome, {user.username}!
            </h5>
            <div className="address-container">
              <span className="address-text">
                Address: {shortAddress(user.address)}
              </span>
              <span className="copy-icon" onClick={handleCopy}>
                <FaCopy className="text-info" />
              </span>
              {copied && <span className="text-success fw-bold">Copied!</span>}
            </div>
            <div className="qr-code-container">
              <QRCodeCanvas value={user.address} size={60} bgColor="#181c2f" fgColor="#1c92d2" />
              <div className="scan-text">
                Scan to send acoin
              </div>
            </div>
            <div className="balance-text">
              Balance: {user.balance} acoin
            </div>
          </div>
        )}
      </div>
      {user && showPopup && (
        <div className="popup-container">
          <div className="card popup-card">
            <h5 className="fw-bold text-white mb-3">Profile Pic Options</h5>
            <button className="btn btn-secondary w-100 mb-2 fw-bold" onClick={() => setShowPopup(false)}>
              View Profile Pic
            </button>
            <input type="file" ref={fileInputRef} className="form-control mb-2" />
            <button className="btn btn-primary w-100 fw-bold" onClick={handleUpload}>
              Upload/Change Profile Pic
            </button>
            <button className="btn btn-outline-danger w-100 mt-2 fw-bold" onClick={() => setShowPopup(false)}>
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default WelcomePage;
