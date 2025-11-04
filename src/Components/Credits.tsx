import { FaUserCircle, FaEnvelope, FaUserSecret } from "react-icons/fa";
import profilePic from "../assets/profile.jpeg";
import { Link } from "react-router-dom";

function Credits() {
  return (
    <div
      className="container py-5"
      style={{
        minHeight: "100vh",
        background: "linear-gradient(135deg, #181c2f 0%, #1c92d2 100%)",
      }}
    >
      <div
        className="card shadow mx-auto p-4"
        style={{
          maxWidth: 500,
          background: "rgba(30,40,60,0.95)",
          borderRadius: "1.2rem",
        }}
      >
        <div className="text-center">
          <img
            src={profilePic}
            alt="Tendai Njanji"
            style={{
              width: 120,
              height: 120,
              borderRadius: "50%",
              marginBottom: 16,
              border: "4px solid #1c92d2",
            }}
          />
          <h3 className="mt-2 fw-bold text-white">
            <FaUserCircle className="me-2 text-white" />
            Tendai Njanji
          </h3>
          <p className="mb-1 fw-bold text-white">
            <FaUserSecret className="me-2 text-white" />
            Blockchain Engineer, Software Engineer, Technopreneur
          </p>
          <p className="mb-1 fw-bold text-white">
            <strong>Nickname:</strong> zimtechguru
          </p>
          <p className="mb-1 fw-bold text-white">
            <FaEnvelope className="me-2 text-white" />
            <strong>Email:</strong>{" "}
            <a
              href="mailto:njanjitendai02@gmail.com"
              style={{ color: "#1c92d2", fontWeight: 700 }}
            >
              njanjitendai02@gmail.com
            </a>
          </p>
        </div>
        <ul className="nav nav-pills flex-column mb-3">
          <li className="nav-item">
            <Link className="nav-link fw-bold text-white" to="/credits">
              <FaUserCircle className="me-2 text-white" /> Credits
            </Link>
          </li>
        </ul>
      </div>
    </div>
  );
}

export default Credits;