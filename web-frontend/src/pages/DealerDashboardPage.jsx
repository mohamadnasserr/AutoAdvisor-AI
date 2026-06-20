import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";

import { getDealerLeads, getDealerships } from "../api";
import logo from "../assets/Logo_AutoAdvisor.png";


function titleCase(value) {
  if (!value) return "Unknown";
  return String(value)
    .replace(/_/g, " ")
    .split(" ")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(" ");
}


function dashboardErrorMessage(requestError) {
  if (/method not allowed/i.test(requestError.message)) {
    return "The dealer dashboard GET routes are not active on the running backend. Restart FastAPI and try again.";
  }
  return requestError.message;
}


export default function DealerDashboardPage() {
  const location = useLocation();
  const [dealerships, setDealerships] = useState([]);
  const [dealerId, setDealerId] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [leads, setLeads] = useState([]);
  const [hasLoaded, setHasLoaded] = useState(false);
  const [loading, setLoading] = useState(false);
  const [loadingDealerships, setLoadingDealerships] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getDealerships()
      .then((data) => setDealerships(Array.isArray(data) ? data : []))
      .catch((requestError) => setError(dashboardErrorMessage(requestError)))
      .finally(() => setLoadingDealerships(false));
  }, []);

  useEffect(() => {
    if (location.state?.loadAll) loadLeads({ allDealers: true });
  }, [location.state]);

  async function loadLeads({ allDealers = false } = {}) {
    setLoading(true);
    setError("");
    try {
      const params = allDealers
        ? {}
        : {
            dealer_id: dealerId || null,
            status: statusFilter || null,
          };
      const data = await getDealerLeads(params);
      setLeads(Array.isArray(data) ? data : []);
      setHasLoaded(true);
    } catch (requestError) {
      setError(dashboardErrorMessage(requestError));
      setLeads([]);
      setHasLoaded(true);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="dealer-dashboard-page">
      <nav>
        <Link className="brand" to="/">
          <img src={logo} alt="AutoAdvisor AI" />
          <span>AutoAdvisor AI</span>
        </Link>
        <Link className="admin-nav-button" to="/">Back to AutoAdvisor</Link>
      </nav>

      <main className="dealer-dashboard-main">
        <header className="dealer-dashboard-hero">
          <p className="eyebrow">AutoAdvisor dealer workspace</p>
          <h1>Dealer Dashboard</h1>
          <h2>View saved buyer interests and dealer inquiry drafts</h2>
          <p>
            Demo dealer dashboard only. Production would require authenticated dealer accounts and tenant isolation.
          </p>
          <p>This dashboard reads saved buyer interests. It does not send messages automatically.</p>
        </header>

        <section className="dealer-dashboard-page-section">
          <div className="panel dealer-dashboard">
            <div className="dealer-dashboard-heading">
              <div>
                <p className="eyebrow">Saved buyer interests</p>
                <h3>Dealer Lead Dashboard Demo</h3>
              </div>
              {hasLoaded && <span>{leads.length} lead{leads.length === 1 ? "" : "s"}</span>}
            </div>

            <div className="dealer-dashboard-controls">
              <label>
                Dealership
                <select
                  value={dealerId}
                  disabled={loadingDealerships}
                  onChange={(event) => setDealerId(event.target.value)}
                >
                  <option value="">
                    {loadingDealerships ? "Loading dealerships..." : "All dealerships"}
                  </option>
                  {dealerships.map((dealership) => (
                    <option key={dealership.id} value={dealership.id}>
                      {dealership.name} · {dealership.location}
                    </option>
                  ))}
                </select>
              </label>

              <label>
                Status filter
                <select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
                  <option value="">Any status</option>
                  <option value="draft_created">Draft created</option>
                </select>
              </label>

              <div className="dealer-dashboard-actions">
                <button disabled={loading} onClick={() => loadLeads()}>
                  {loading ? "Working..." : "Load dealer leads"}
                </button>
                <button className="secondary" disabled={loading} onClick={() => loadLeads({ allDealers: true })}>
                  {loading ? "Working..." : "Load all leads"}
                </button>
              </div>
            </div>

            {error && <div className="notice error">{error}</div>}
            {hasLoaded && !loading && !error && leads.length === 0 && (
              <p className="muted">No saved interests found yet. Save interest on a car first.</p>
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
                    <div><dt>Dealership</dt><dd>{lead.dealership_name || "Not assigned"}</dd></div>
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
