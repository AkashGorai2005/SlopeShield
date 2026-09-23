import { useEffect, useRef, useState } from "react";
import { Link } from "../lib/navigation";
import { useProjectData } from "@/context/ProjectDataContext";
import { formatRainfall } from "@/utils/formatters";

import {
  Search,
  Bell,
  UserRound,
  Map,
  ArrowUpRight,
  AlertTriangle,
  CloudRain,
  ChevronRight,
} from "lucide-react";

import "./Home.css";

export default function Home() {
  const { summary, risk, rainfall, warnings } = useProjectData();
  const [notificationOpen, setNotificationOpen] = useState(false);
  const panelRef = useRef(null);

  useEffect(() => {
    function handlePointerDown(event) {
      if (
        panelRef.current &&
        !panelRef.current.contains(event.target)
      ) {
        setNotificationOpen(false);
      }
    }

    document.addEventListener("mousedown", handlePointerDown);

    return () => {
      document.removeEventListener(
        "mousedown",
        handlePointerDown
      );
    };
  }, []);

  return (
    <main className="slope-home">

      {/* =====================================================
          HERO
      ===================================================== */}
<section className="hero">

  {/* HERO IMAGE OVERLAY */}
  <div className="hero-overlay" />

  <div className="hero-leaf hero-leaf-left" aria-hidden="true">
    <img src="/images/leaf.png" alt="" />
  </div>

  <div className="hero-leaf hero-leaf-right" aria-hidden="true">
    <img src="/images/leaf.png" alt="" />
  </div>

  {/* =================================================
      NAVBAR
  ================================================= */}
        <header className="slope-navbar">

          {/* BRAND */}
          <Link to="/" className="brand">

            <div className="brand-logo">
              <img
                src="/logo.png"
                alt="SLOPESHIELD NER"
              />
            </div>

            <span className="brand-name">
              SLOPESHIELD NER
            </span>

          </Link>


          {/* NAVIGATION */}
          <nav className="main-nav">

            <Link
              to="/"
              className="nav-link active"
            >
              Home
            </Link>

            <Link
              to="/dashboard"
              className="nav-link"
            >
              Dashboard
            </Link>

            <Link
              to="/about"
              className="nav-link"
            >
              About
            </Link>

            <Link
              to="/risk-map"
              className="nav-link"
            >
              Map
            </Link>

          </nav>


          {/* RIGHT ACTIONS */}
          <div className="nav-actions">

            <button
              className="circle-action"
              aria-label="Search"
            >
              <Search size={19} />
            </button>


            {/* NOTIFICATIONS */}
            <div
              ref={panelRef}
              className="notification-wrap"
            >

              <button
                className="circle-action notification-button"
                aria-label="Notifications"
                onClick={() =>
                  setNotificationOpen(
                    (value) => !value
                  )
                }
              >
                <Bell size={18} />

                <span className="notification-dot" />
              </button>


              {notificationOpen && (
                <div className="notification-panel">

                  <div className="notification-header">
                    <span>MONITORING UPDATES</span>
                    <strong>Notifications</strong>
                  </div>

                  {warnings.slice(0, 4).map((item) => (
                    <div
                      key={item.area}
                      className={`notification-item ${item.severity}`}
                    >

                      <div className="notification-status">
                        <span />
                      </div>

                      <div>
                        <div className="notification-label">{item.riskLevel} risk</div>

                        <div className="notification-area">
                          {item.location}
                        </div>

                        <div className="notification-detail">
                          {formatRainfall(item.rainfall)} rainfall · {item.status || "active"}
                        </div>
                      </div>

                    </div>
                  ))}

                  {warnings.length === 0 && <div className="notification-detail">No active alerts.</div>}

                </div>
              )}

            </div>


            {/* PROFILE */}
            <Link
              to="/login"
              className="profile-action"
            >
              <UserRound size={18} />
            </Link>

          </div>

        </header>


        {/* =================================================
            HERO CONTENT
        ================================================= */}

        <div className="hero-content">

          <div className="hero-eyebrow">
            AI-POWERED LANDSLIDE RISK INTELLIGENCE
          </div>

          <h1>
            SLOPESHIELD NER
            <br />
          
          </h1>

          <p className="hero-description">
            Monitoring rainfall, terrain, elevation,
            land cover, geology and historical landslide
            patterns to identify areas of elevated risk
            across Northeast India.
          </p>


          <div className="hero-buttons">

            <Link
              to="/risk-map"
              className="hero-button primary"
            >
              <Map size={17} />

              Explore Risk Map

              <ArrowUpRight size={17} />
            </Link>


            <Link
              to="/dashboard"
              className="hero-button secondary"
            >
              View Dashboard

              <ArrowUpRight size={17} />
            </Link>

          </div>

        </div>


        {/* =================================================
            FLOATING LOCATION CARD
        ================================================= */}

        <div className="location-glass">

          <div className="location-top">

            <span className="location-pin">
              ●
            </span>

            Northeast India

            <ChevronRight size={16} />

          </div>


          <div className="location-image">

            <img
              src="/images/northeast-landscape.jpg"
              alt="Northeast India landscape"
            />

          </div>


          <div className="location-title">
            Smarter monitoring.
            <br />
            Safer tomorrow.
          </div>


          <div className="location-line" />

        </div>


        {/* =================================================
            RISK OVERVIEW
        ================================================= */}

        <div className="risk-overview">

          <div className="risk-heading">

            <span className="risk-heading-line" />

            <div>
              <small>
                REGIONAL STATUS
              </small>

              <h3>
                Risk Overview
              </h3>
            </div>

          </div>


          <div className="risk-items">

            <Risk
              color="low"
              label="Low"
              value={risk?.distribution?.find((item) => item.level === "low")?.count ?? 0}
            />

            <Risk
              color="moderate"
              label="Moderate"
              value={risk?.distribution?.find((item) => item.level === "moderate")?.count ?? 0}
            />

            <Risk
              color="high"
              label="High"
              value={risk?.distribution?.find((item) => item.level === "high")?.count ?? 0}
            />

            <Risk
              color="critical"
              label="Critical"
              value={risk?.distribution?.find((item) => item.level === "critical")?.count ?? 0}
            />

          </div>


          <div className="risk-divider" />


          <div className="attention">

            <AlertTriangle size={24} />

            <div>

              <small>
                Areas Requiring Attention
              </small>

              <strong>
                {warnings.length > 0 ? warnings.slice(0, 3).map((item) => item.location).join(" · ") : "No active alerts"}
              </strong>

            </div>

            <ChevronRight size={18} />

          </div>


          <div className="risk-divider" />


          <div className="rainfall">

            <CloudRain size={25} />

            <div>

              <small>
                Rainfall Status
              </small>

              <strong>
                {formatRainfall(rainfall?.status?.last24h)}
              </strong>

              <span>
                {rainfall?.status?.headline || "No rainfall data available"}
              </span>

            </div>

            <ChevronRight size={18} />

          </div>

        </div>

      </section>


      {/* =====================================================
          LANDSCAPE STORY
      ===================================================== */}

      <section className="landscape-story">



        {/* STORY CONTENT */}

        <div className="story-content">

          <div className="story-eyebrow">
            UNDERSTANDING THE LANDSCAPE
          </div>


          <h2>
            Every slope
            <br />
            <em>tells a story.</em>
          </h2>


          <p className="story-description">
            SLOPESHIELD NER brings together rainfall,
            terrain, elevation, geology and historical
            landslide information to understand where
            the landscape may be becoming vulnerable.
          </p>


          <div className="data-elements">


            <div className="data-element">

              <span className="data-number">
                01
              </span>

              <div>
                <h3>
                  Rainfall
                </h3>

                <p>
                  Monitoring precipitation patterns
                </p>
              </div>

            </div>


            <div className="data-element">

              <span className="data-number">
                02
              </span>

              <div>
                <h3>
                  Terrain
                </h3>

                <p>
                  Understanding slope and elevation
                </p>
              </div>

            </div>


            <div className="data-element">

              <span className="data-number">
                03
              </span>

              <div>
                <h3>
                  Geology
                </h3>

                <p>
                  Reading the characteristics of the land
                </p>
              </div>

            </div>


            <div className="data-element">

              <span className="data-number">
                04
              </span>

              <div>
                <h3>
                  History
                </h3>

                <p>
                  Learning from previous landslides
                </p>
              </div>

            </div>


          </div>

        </div>

      </section>

    </main>
  );
}


/* =========================================================
   RISK COMPONENT
========================================================= */

function Risk({ color, label, value }) {
  return (
    <div className="risk-item">

      <div
        className={`risk-dot ${color}`}
      />

      <span>
        {label}
      </span>

      <strong>
        {value}
      </strong>

      <small>
        areas
      </small>

    </div>
  );
}