import React from "react";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";

const Profile = () => {
  return (
    <div>
      <Navbar />
      <div
        style={{ padding: "4rem 2rem", minHeight: "60vh", textAlign: "center" }}
      >
        <h1>👤 User Profile</h1>
        <p style={{ fontSize: "1.2rem", color: "#666", marginTop: "1rem" }}>
          Manage your account settings.
        </p>
      </div>
      <Footer />
    </div>
  );
};

export default Profile;
