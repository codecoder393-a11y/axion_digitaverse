import { Link } from "react-router-dom";
import {
  FaUserSecret,
  FaMoneyBillWave,
  FaInfoCircle,
} from "react-icons/fa";

import { GlassPanel } from './SharedUI';

function Sidebar() {
  return (
    <div style={{ minHeight: '100vh', width: 220, position: 'fixed', top: 0, left: 0, zIndex: 1000 }}>
      <GlassPanel style={{ height: '100%', borderRadius: 0, borderTopRightRadius: 12, borderBottomRightRadius: 12 }} className="p-3">
        <h5 className="mb-4 text-center">Management</h5>
        <ul className="nav flex-column">
          <li className="nav-item mb-2">
            <Link className="nav-link text-white d-flex align-items-center" to="/agents">
              <FaUserSecret className="me-2" /> Agents
            </Link>
          </li>
          <li className="nav-item mb-2">
            <Link className="nav-link text-white d-flex align-items-center" to="/register-agent">
              <FaUserSecret className="me-2" /> Register Agent
            </Link>
          </li>
          <li className="nav-item mb-2">
            <Link className="nav-link text-white d-flex align-items-center" to="/agent-deposit">
              <FaMoneyBillWave className="me-2" /> Agent Deposit
            </Link>
          </li>
          <li className="nav-item mb-2">
            <Link className="nav-link text-white d-flex align-items-center" to="/about">
              <FaInfoCircle className="me-2" /> About
            </Link>
          </li>
        </ul>
      </GlassPanel>
    </div>
  );
}

export default Sidebar;