import { FaInfoCircle, FaWallet, FaUserSecret, FaCode } from "react-icons/fa";

function About() {
  return (
    <div className="container py-5">
      <h2 className="mb-4 text-center text-white">
        <FaInfoCircle className="me-2" /> About Axion Digitaverse Ecosystem
      </h2>
      <div className="card shadow mx-auto p-4" style={{ maxWidth: 700 }}>
        <ul className="list-unstyled fs-5">
          <li className="fw-bold text-white">
            <FaWallet className="me-2" />
            <strong>Wallet:</strong> Every user gets a secure wallet with acoin balance and unique address.
          </li>
          <li className="mt-3 fw-bold text-white">
            <FaUserSecret className="me-2 fw-bold text-white" />
            <strong>Agents:</strong> Buy Acoin from trusted agents to fund your activities.
          </li>
          <li className="mt-3 fw-bold text-white">
            <FaCode className="me-2 fw-bold text-warning" />
            <strong>Python IDE & Smart Contracts:</strong> Write and run Python code, deploy smart contracts, and build dApps.
          </li>
          <li className="mt-3 fw-bold text-white">
            <FaInfoCircle className="me-2 fw-bold text-white" />
            <strong>Privacy:</strong> Your private key is only shown to you and never stored on the blockchain.
          </li>
        </ul>
        <div className="mt-4 fw-bold text-white" style={{ fontSize: 15 }}>
          Axion Digitaverse is a secure, decentralized platform for identity, payments, and smart contracts.
          <br />
          <strong>Tip:</strong> Keep your private key safe. Use acoin for payments, loans, and dApps!
        </div>
      </div>
    </div>
  );
}

export default About;