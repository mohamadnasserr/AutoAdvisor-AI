import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import {
  dealerLogin,
  getDealerProfile,
  getMyDealerLeads,
} from "../api";
import logo from "../assets/Logo_AutoAdvisor.png";


const DEALER_TOKEN_KEY = "autoadvisor_dealer_token";
const DEMO_ACCOUNTS = [
  "beirut@autoadvisor.demo / demo123",
  "jounieh@autoadvisor.demo / demo123",
  "tripoli@autoadvisor.demo / demo123",
];


function titleCase(value) {
  if (!value) return "Unknown";
  return String(value)
    .replace(/_/g, " ")
    .split(" ")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(" ");
}


function errorMessage(requestError) {
  if (/dealer authentication required|invalid or expired|account is unavailable/i.test(requestError.message)) {
    return "Your dealer session has expired. Please log in again.";
  }
  if (/method not allowed|not found/i.test(requestError.message)) {
    return "The dealer portal routes are not active on the running backend. Restart FastAPI and try again.";
  }
  return requestError.message;
}


export default function DealerDashboardPage() {
  const [token, setToken] = useState(() => localStorage.getItem(DEALER_TOKEN_KEY) || "");
  const [profile, setProfile] = useState(null);
  const [leads, setLeads] = useState([]);
  const [email, setEmail] = useState("beirut@autoadvisor.demo");
  const [password, setPassword] = useState("demo123");
  const [statusFilter, setStatusFilter] = useState("");
  const [checkingSession, setCheckingSession] = useState(Boolean(token));
  const [loginLoading, setLoginLoading] = useState(false);
  const [leadsLoading, setLeadsLoading] = useState(false);
  const [hasLoaded, setHasLoaded] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!token) {
      setCheckingSession(false);
      return;
    }

    Promise.all([getDealerProfile(token), getMyDealerLeads(token)])
      .then(([dealerProfile, dealerLeads]) => {
        setProfile(dealerProfile);
        setLeads(Array.isArray(dealerLeads) ? dealerLeads : []);
        setHasLoaded(true);
      })
      .catch((requestError) => {
        localStorage.removeItem(DEALER_TOKEN_KEY);
        setToken("");
        setProfile(null);
        setLeads([]);
        setError(errorMessage(requestError));
      })
      .finally(() => setCheckingSession(false));
  }, [token]);

  async function submitLogin(event) {
    event.preventDefault();
    setLoginLoading(true);
    setError("");
    try {
      const loginResult = await dealerLogin(email, password);
      localStorage.setItem(DEALER_TOKEN_KEY, loginResult.access_token);
      setProfile(loginResult.dealer_user);
      setToken(loginResult.access_token);
    } catch (requestError) {
      setError(errorMessage(requestError));
    } finally {
      setLoginLoading(false);
    }
  }

  async function refreshMyLeads() {
    setLeadsLoading(true);
    setError("");
    try {
      const data = await getMyDealerLeads(token, {
        status: statusFilter || null,
      });
      setLeads(Array.isArray(data) ? data : []);
      setHasLoaded(true);
    } catch (requestError) {
      const message = errorMessage(requestError);
      setError(message);
      if (/session has expired/i.test(message)) logout();
    } finally {
      setLeadsLoading(false);
    }
  }

  function logout() {
    localStorage.removeItem(DEALER_TOKEN_KEY);
    setToken("");
    setProfile(null);
    setLeads([]);
    setHasLoaded(false);
    setError("");
  }

  if (checkingSession) {
    return (
      <div className="dealer-dashboard-page dealer-login-page">
        <div className="panel dealer-session-loading">Checking dealer session...</div>
      </div>
    );
  }

  if (!token || !profile) {
    return (
      <div className="dealer-dashboard-page dealer-login-page">
        <nav>
          <Link className="brand" to="/">
            <img src={logo} alt="AutoAdvisor AI" />
            <span>AutoAdvisor AI</span>
          </Link>
          <Link className="admin-nav-button" to="/">Back to AutoAdvisor</Link>
        </nav>

        <main className="dealer-login-main">
          <div className="dealer-login-glow" />
          <section className="dealer-login-shell">
            <div className="dealer-login-copy">
              <p className="eyebrow">Protected dealership portal</p>
              <h1>Dealer Dashboard</h1>
              <h2>View saved buyer interests and dealer inquiry drafts</h2>
              <p>Dealer portal demo. Each dealership account can only view leads for its own inventory.</p>
              <p>Saved buyer interests are inquiry drafts only. AutoAdvisor does not send messages automatically.</p>
            </div>

            <div className="panel dealer-login-card">
              <h3>Dealer login</h3>
              <form onSubmit={submitLogin}>
                <label>
                  Email
                  <input
                    type="email"
                    value={email}
                    onChange={(event) => setEmail(event.target.value)}
                    autoComplete="username"
                    required
                  />
                </label>
                <label>
                  Password
                  <input
                    type="password"
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    autoComplete="current-password"
                    required
                  />
                </label>
                <button type="submit" disabled={loginLoading}>
                  {loginLoading ? "Signing in..." : "Sign in to dealer portal"}
                </button>
              </form>

              {error && <div className="notice error">{error}</div>}
              <div className="demo-account-hints">
                <strong>Demo accounts</strong>
                {DEMO_ACCOUNTS.map((account) => <code key={account}>{account}</code>)}
              </div>
            </div>
          </section>
        </main>
      </div>
    );
  }

  return (
    <div className="dealer-dashboard-page">
      <nav>
        <Link className="brand" to="/">
          <img src={logo} alt="AutoAdvisor AI" />
          <span>AutoAdvisor AI</span>
        </Link>
        <div className="dealer-account-nav">
          <span>{profile.email}</span>
          <button className="secondary" onClick={logout}>Logout</button>
          <Link className="admin-nav-button" to="/">Back to AutoAdvisor</Link>
        </div>
      </nav>

      <main className="dealer-dashboard-main">
        <header className="dealer-dashboard-hero">
          <p className="eyebrow">Protected dealership portal</p>
          <h1>Dealer Dashboard</h1>
          <h2>{profile.dealership_name}</h2>
          <p>Logged in as {profile.email}</p>
          <p>Dealer portal demo. Each dealership account can only view leads for its own inventory.</p>
          <p>Saved buyer interests are inquiry drafts only. AutoAdvisor does not send messages automatically.</p>
        </header>

        <section className="dealer-dashboard-page-section">
          <div className="panel dealer-dashboard">
            <div className="dealer-dashboard-heading">
              <div>
                <p className="eyebrow">My dealership leads</p>
                <h3>{profile.full_name}</h3>
              </div>
              {hasLoaded && <span>{leads.length} lead{leads.length === 1 ? "" : "s"}</span>}
            </div>

            <div className="dealer-dashboard-controls dealer-tenant-controls">
              <label>
                Status filter
                <select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
                  <option value="">Any status</option>
                  <option value="draft_created">Draft created</option>
                </select>
              </label>
              <button disabled={leadsLoading} onClick={refreshMyLeads}>
                {leadsLoading ? "Refreshing..." : "Refresh my leads"}
              </button>
            </div>

            {error && <div className="notice error">{error}</div>}
            {hasLoaded && !leadsLoading && !error && leads.length === 0 && (
              <p className="muted">No buyer interests for your dealership yet.</p>
            )}

            <div className="dealer-lead-grid">
              {leads.map((lead) => (
                <article className="dealer-lead-card" key={lead.lead_id}>
                  <div className="dealer-lead-card-heading">
                    <div>
                      <small>Lead #{lead.lead_id}</small>
                      <h4>{lead.customer_name || "Buyer name not provided"}</h4>
                    </div>
                    <span className="lead-status">{titleCase(lead.status)}</span>
                  </div>
                  <dl>
                    <div><dt>Phone</dt><dd>{lead.customer_phone || "Not provided"}</dd></div>
                    <div><dt>Email</dt><dd>{lead.customer_email || "Not provided"}</dd></div>
                    <div><dt>Preferred contact</dt><dd>{titleCase(lead.preferred_contact_method || "Not provided")}</dd></div>
                    <div><dt>Interested car</dt><dd>{lead.car_title}</dd></div>
                    <div><dt>Car price</dt><dd>{lead.car_price_usd == null ? "Unavailable" : `$${Number(lead.car_price_usd).toLocaleString()}`}</dd></div>
                    <div><dt>Budget</dt><dd>{lead.budget == null ? "Not provided" : `$${Number(lead.budget).toLocaleString()}`}</dd></div>
                    <div><dt>Location</dt><dd>{lead.user_location || "Not provided"}</dd></div>
                  </dl>
                  <p><strong>Notes:</strong> {lead.notes || "No notes provided."}</p>
                  <div className="lead-message-draft">
                    <strong>Inquiry draft</strong>
                    <p>{lead.message_draft}</p>
                  </div>
                </article>
              ))}
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
