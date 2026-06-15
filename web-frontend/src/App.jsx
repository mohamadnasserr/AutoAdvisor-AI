import { useEffect, useMemo, useState } from "react";
import logo from "./assets/Logo_AutoAdvisor.png";
import {
  API_BASE_URL,
  BACKEND_LABEL,
  apiGet,
  apiPost,
  compareCars,
  uploadImage,
} from "./api";

const gears = [
  ["D", "Drive", "AI assistant and recommendations", "drive"],
  ["P", "Park", "Browse curated inventory", "park"],
  ["N", "Neutral", "Compare cars", "neutral"],
  ["R", "Reverse", "Check fair price", "reverse"],
  ["S", "Save", "Save interest and prepare dealer inquiry drafts", "save"],
];

const defaultPriceDetails = {
  brand: "Toyota",
  model: "Yaris",
  year: 2018,
  mileage_km: 60000,
  fuel_type: "Petrol",
  transmission_type: "Automatic",
  vehicle_age: 8,
  engine: 1200,
  mileage: 18,
  max_power: 82,
  seats: 5,
};

function scrollTo(id) {
  document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
}

function LoadingButton({ loading, children, ...props }) {
  return (
    <button {...props} disabled={loading || props.disabled}>
      {loading ? "Working…" : children}
    </button>
  );
}

function Notice({ error, children, type = "info" }) {
  if (!error && !children) return null;
  return <div className={`notice ${error ? "error" : type}`}>{error || children}</div>;
}

function SaveInterestForm({
  carId,
  defaultBudget = "",
  allowCarId = false,
  initiallyOpen = false,
}) {
  const [open, setOpen] = useState(initiallyOpen);
  const [form, setForm] = useState({
    selected_car_id: carId || 1,
    customer_name: "",
    customer_phone: "",
    customer_email: "",
    preferred_contact_method: "phone",
    user_location: "Lebanon",
    budget: defaultBudget,
    notes: "",
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const update = (key, value) => setForm((current) => ({ ...current, [key]: value }));

  async function submit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);
    try {
      setResult(
        await apiPost("/dealer/leads", {
          ...form,
          selected_car_id: Number(form.selected_car_id),
          budget: form.budget ? Number(form.budget) : null,
        }),
      );
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }

  if (!open) {
    return (
      <button className="save-interest-trigger" onClick={() => setOpen(true)}>
        Save Interest
      </button>
    );
  }

  return (
    <div className="save-interest">
      <div className="save-interest-heading">
        <strong>Save Interest</strong>
        {!initiallyOpen && <button className="text-button" onClick={() => setOpen(false)}>Close</button>}
      </div>
      <p className="muted">
        This saves a buyer interest draft. No message is sent automatically.
      </p>
      <form onSubmit={submit}>
        <div className="save-interest-grid">
          {allowCarId && <Field label="Selected car ID"><input type="number" min="1" value={form.selected_car_id} onChange={(e) => update("selected_car_id", e.target.value)} /></Field>}
          <Field label="Name"><input value={form.customer_name} onChange={(e) => update("customer_name", e.target.value)} placeholder="Optional" /></Field>
          <Field label="Phone"><input value={form.customer_phone} onChange={(e) => update("customer_phone", e.target.value)} placeholder="Optional" /></Field>
          <Field label="Email"><input type="email" value={form.customer_email} onChange={(e) => update("customer_email", e.target.value)} placeholder="Optional" /></Field>
          <Field label="Preferred contact method"><select value={form.preferred_contact_method} onChange={(e) => update("preferred_contact_method", e.target.value)}>{["phone", "email", "WhatsApp"].map((item) => <option key={item}>{item}</option>)}</select></Field>
          <Field label="Location"><input value={form.user_location} onChange={(e) => update("user_location", e.target.value)} /></Field>
          <Field label="Budget"><input type="number" value={form.budget} onChange={(e) => update("budget", e.target.value)} placeholder="Optional" /></Field>
          <Field label="Notes"><textarea value={form.notes} onChange={(e) => update("notes", e.target.value)} placeholder="Optional questions or preferences" /></Field>
        </div>
        <LoadingButton loading={loading} type="submit">Save buyer interest draft</LoadingButton>
      </form>
      <Notice error={error} />
      {result && (
        <div className="saved-lead-result">
          <span className="assistant-label">Interest saved · draft only</span>
          <h4>Lead #{result.lead_id} · Car #{result.selected_car_id}</h4>
          <p>
            <strong>Buyer:</strong> {result.customer_name || "Name not provided"} ·{" "}
            {result.customer_phone || "Phone not provided"} ·{" "}
            {result.customer_email || "Email not provided"}
          </p>
          <p>
            <strong>Dealer:</strong> {result.dealership_name || "Not available"} ·{" "}
            {result.dealership_location || "Location unavailable"} ·{" "}
            {result.dealership_phone || result.dealership_email || "Contact unavailable"}
          </p>
          <div className="draft">{result.message_draft}</div>
        </div>
      )}
    </div>
  );
}

function CarCard({ car }) {
  return (
    <article className="car-card">
      {car.image_url && (
        <img
          src={car.image_url}
          alt={`Representative ${car.make} ${car.model}`}
          onError={(event) => {
            event.currentTarget.style.display = "none";
          }}
        />
      )}
      <div className="car-card-body">
        <div className="eyebrow">
          #{car.id} · {car.listing_type || "listing"} · {car.availability_status || "unknown"}
        </div>
        <h3>
          {car.year} {car.make} {car.model} {car.trim || ""}
        </h3>
        <div className="car-metrics">
          <strong>${Number(car.price_usd || 0).toLocaleString()}</strong>
          <span>
            {car.mileage_km === null || car.mileage_km === undefined
              ? "Mileage unavailable"
              : `${Number(car.mileage_km).toLocaleString()} km`}
          </span>
        </div>
        <p>
          {car.body_type} · {car.fuel} · {car.transmission}
        </p>
        <small>{car.region}</small>
        <SaveInterestForm carId={car.id} defaultBudget={car.price_usd || ""} />
      </div>
    </article>
  );
}

function CarGrid({ cars, empty = "No cars to display." }) {
  if (!cars?.length) return <p className="muted">{empty}</p>;
  return (
    <>
      <p className="representative-note">
        Images are representative demo visuals, not verified listing photos.
      </p>
      <div className="car-grid">
        {cars.map((car) => (
          <CarCard key={car.id} car={car} />
        ))}
      </div>
    </>
  );
}

function SectionHeader({ gear, title, description }) {
  return (
    <div className="section-heading">
      <span className="gear-badge">{gear}</span>
      <div>
        <p className="eyebrow">{title}</p>
        <h2>{description}</h2>
      </div>
    </div>
  );
}

function Field({ label, children }) {
  return (
    <label>
      <span>{label}</span>
      {children}
    </label>
  );
}

function PriceFields({ details, setDetails }) {
  const update = (key, value) => setDetails((current) => ({ ...current, [key]: value }));
  return (
    <div className="form-grid">
      <Field label="Brand"><input value={details.brand} onChange={(e) => update("brand", e.target.value)} /></Field>
      <Field label="Model"><input value={details.model} onChange={(e) => update("model", e.target.value)} /></Field>
      <Field label="Year"><input type="number" value={details.year} onChange={(e) => update("year", e.target.value)} /></Field>
      <Field label="Mileage (km)"><input type="number" value={details.mileage_km} onChange={(e) => update("mileage_km", e.target.value)} /></Field>
      <Field label="Fuel type">
        <select value={details.fuel_type} onChange={(e) => update("fuel_type", e.target.value)}>
          {["Petrol", "Diesel", "CNG", "LPG", "Electric"].map((item) => <option key={item}>{item}</option>)}
        </select>
      </Field>
      <Field label="Transmission">
        <select value={details.transmission_type} onChange={(e) => update("transmission_type", e.target.value)}>
          {["Automatic", "Manual"].map((item) => <option key={item}>{item}</option>)}
        </select>
      </Field>
      <Field label="Vehicle age"><input type="number" value={details.vehicle_age} onChange={(e) => update("vehicle_age", e.target.value)} /></Field>
      <Field label="Engine (cc)"><input type="number" value={details.engine} onChange={(e) => update("engine", e.target.value)} /></Field>
      <Field label="Fuel economy"><input type="number" step="0.1" value={details.mileage} onChange={(e) => update("mileage", e.target.value)} /></Field>
      <Field label="Max power"><input type="number" value={details.max_power} onChange={(e) => update("max_power", e.target.value)} /></Field>
      <Field label="Seats"><input type="number" value={details.seats} onChange={(e) => update("seats", e.target.value)} /></Field>
    </div>
  );
}

function pricePayload(details) {
  return {
    brand: details.brand,
    model: details.model,
    vehicle_age: Number(details.vehicle_age),
    km_driven: Number(details.mileage_km),
    fuel_type: details.fuel_type,
    transmission_type: details.transmission_type,
    mileage: Number(details.mileage),
    engine: Number(details.engine),
    max_power: Number(details.max_power),
    seats: Number(details.seats),
  };
}

function PriceResult({ result, details }) {
  if (!result) return null;
  const confidence = result.confidence ?? result.model_r2;
  const label = confidence >= 0.8 ? "High confidence" : confidence >= 0.6 ? "Medium confidence" : "Low confidence";
  return (
    <div className="assistant-card result-card">
      <span className="assistant-label">AutoAdvisor estimate</span>
      <h3>
        {details.year} {details.brand} {details.model} · {Number(details.mileage_km).toLocaleString()} km
      </h3>
      <div className="price-result">
        <strong>${Number(result.estimated_price_usd).toLocaleString()}</strong>
        <span>
          Fair range: ${Number(result.low_estimate_usd).toLocaleString()} to ${Number(result.high_estimate_usd).toLocaleString()}
        </span>
        <span>{label}</span>
      </div>
      <p className="warning-text">{result.disclaimer}</p>
      <details><summary>Technical price model details</summary><pre>{JSON.stringify(result, null, 2)}</pre></details>
    </div>
  );
}

function DriveSection() {
  const examples = [
    "I need a reliable used SUV under $15,000 in Beirut",
    "Compare Toyota Corolla and Kia Picanto",
    "Is this 2018 Hyundai Tucson overpriced?",
    "Connect me with the dealer for Toyota Corolla",
  ];
  const [messages, setMessages] = useState([
    { role: "assistant", content: "Welcome to Drive. Tell me what kind of car you are looking for." },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function send(message) {
    if (!message.trim() || loading) return;
    setError("");
    setMessages((current) => [...current, { role: "user", content: message }]);
    setInput("");
    setLoading(true);
    try {
      const result = await apiPost("/chat", { message, session_id: "react-demo-session" });
      setMessages((current) => [...current, { role: "assistant", content: result.answer, meta: result }]);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section id="drive">
      <SectionHeader gear="D" title="Drive" description="Ask the AI car-buying assistant" />
      <p className="section-copy">Intent routing, inventory search, chat memory, recommendations, and optional OpenAI response polishing.</p>
      <div className="prompt-row">{examples.map((item) => <button className="prompt-chip" key={item} onClick={() => send(item)}>{item}</button>)}</div>
      <div className="chat-shell">
        <div className="chat-log">
          {messages.map((message, index) => (
            <div className={`message ${message.role}`} key={`${message.role}-${index}`}>
              <div className="message-bubble">{message.content}</div>
              {message.meta?.recommended_cars?.length > 0 && <CarGrid cars={message.meta.recommended_cars} />}
              {message.meta && <details><summary>Debug details</summary><pre>{JSON.stringify({ intent: message.meta.intent, extracted_preferences: message.meta.extracted_preferences }, null, 2)}</pre></details>}
            </div>
          ))}
          {loading && <div className="message assistant"><div className="message-bubble">Reviewing your request…</div></div>}
        </div>
        <Notice error={error} />
        <form className="chat-input" onSubmit={(e) => { e.preventDefault(); send(input); }}>
          <input value={input} onChange={(e) => setInput(e.target.value)} placeholder="Ask about cars, comparisons, fair price, or a dealer draft…" />
          <LoadingButton loading={loading} type="submit">Send</LoadingButton>
        </form>
      </div>
    </section>
  );
}

function ParkSection() {
  const [filters, setFilters] = useState({ listing_type: "Any", budget_max: "", make: "", body_type: "Any", fuel: "Any", transmission: "Any", region: "" });
  const [cars, setCars] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const update = (key, value) => setFilters((current) => ({ ...current, [key]: value }));

  async function load(path, params = {}) {
    setLoading(true); setError("");
    try {
      const result = await apiGet(path, params);
      setCars(Array.isArray(result) ? result : result.results || []);
    } catch (requestError) { setError(requestError.message); }
    finally { setLoading(false); }
  }

  return (
    <section id="park">
      <SectionHeader gear="P" title="Park" description="Explore the AutoAdvisor inventory" />
      <p className="section-copy">This is curated demo inventory, not live scraped marketplace data.</p>
      <div className="panel">
        <div className="form-grid compact">
          <Field label="Listing type"><select value={filters.listing_type} onChange={(e) => update("listing_type", e.target.value)}>{["Any", "used", "new"].map((v) => <option key={v}>{v}</option>)}</select></Field>
          <Field label="Budget max"><input type="number" value={filters.budget_max} onChange={(e) => update("budget_max", e.target.value)} placeholder="Optional" /></Field>
          <Field label="Make"><input value={filters.make} onChange={(e) => update("make", e.target.value)} placeholder="Optional" /></Field>
          <Field label="Body type"><select value={filters.body_type} onChange={(e) => update("body_type", e.target.value)}>{["Any", "Sedan", "SUV", "Hatchback", "Coupe", "Pickup", "Van"].map((v) => <option key={v}>{v}</option>)}</select></Field>
          <Field label="Fuel"><select value={filters.fuel} onChange={(e) => update("fuel", e.target.value)}>{["Any", "Petrol", "Hybrid", "Diesel", "Electric"].map((v) => <option key={v}>{v}</option>)}</select></Field>
          <Field label="Transmission"><select value={filters.transmission} onChange={(e) => update("transmission", e.target.value)}>{["Any", "Automatic", "Manual"].map((v) => <option key={v}>{v}</option>)}</select></Field>
          <Field label="Region"><input value={filters.region} onChange={(e) => update("region", e.target.value)} placeholder="Optional" /></Field>
        </div>
        <div className="button-row">
          <LoadingButton loading={loading} onClick={() => load("/search/cars", filters)}>Search inventory</LoadingButton>
          <LoadingButton loading={loading} className="secondary" onClick={() => load("/cars")}>Show all inventory</LoadingButton>
        </div>
        <Notice error={error}>{cars.length ? `Showing ${cars.length} cars.` : ""}</Notice>
      </div>
      <CarGrid cars={cars} empty="Search or show all inventory to begin." />
    </section>
  );
}

function NeutralSection() {
  const [ids, setIds] = useState("1, 2");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  async function submit() {
    const carIds = ids.split(",").map((id) => Number(id.trim())).filter(Number.isInteger);
    setLoading(true); setError("");
    try { setResult(await compareCars(carIds)); } catch (requestError) { setError(requestError.message); }
    finally { setLoading(false); }
  }
  return (
    <section id="neutral">
      <SectionHeader gear="N" title="Neutral" description="Compare 2 to 5 inventory cars" />
      <div className="panel inline-panel">
        <Field label="Comma-separated car IDs"><input value={ids} onChange={(e) => setIds(e.target.value)} /></Field>
        <LoadingButton loading={loading} onClick={submit}>Compare cars</LoadingButton>
      </div>
      <Notice error={error} />
      {result && <>
        <div className="assistant-card"><span className="assistant-label">Verdict</span><p>{result.final_verdict}</p></div>
        <div className="comparison-grid">{result.cars.map((car) => <article className="comparison-card" key={car.id}><h3>{car.title}</h3><p>${Number(car.price_usd).toLocaleString()} · {car.mileage_km?.toLocaleString() || 0} km</p><p>{car.body_type} · {car.fuel} · {car.transmission}</p><h4>Strengths</h4><ul>{car.strengths.map((item) => <li key={item}>{item}</li>)}</ul><h4>Risks</h4><ul>{car.risks.map((item) => <li key={item}>{item}</li>)}</ul><p><strong>Best use:</strong> {car.best_use_case}</p></article>)}</div>
      </>}
    </section>
  );
}

function ReverseSection() {
  const [details, setDetails] = useState(defaultPriceDetails);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  async function submit() {
    setLoading(true); setError("");
    try { setResult(await apiPost("/price/used-car", pricePayload(details))); } catch (requestError) { setError(requestError.message); }
    finally { setLoading(false); }
  }
  return (
    <section id="reverse">
      <SectionHeader gear="R" title="Reverse" description="Check a used-car fair price" />
      <div className="panel"><PriceFields details={details} setDetails={setDetails} /><LoadingButton loading={loading} onClick={submit}>Estimate fair price</LoadingButton><Notice error={error} /></div>
      <PriceResult result={result} details={details} />
    </section>
  );
}

function ImageEvaluationSection() {
  const [file, setFile] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [details, setDetails] = useState(defaultPriceDetails);
  const [priceResult, setPriceResult] = useState(null);
  const [similar, setSimilar] = useState(null);
  const [loading, setLoading] = useState("");
  const [error, setError] = useState("");
  const preview = useMemo(() => file ? URL.createObjectURL(file) : "", [file]);
  useEffect(() => () => { if (preview) URL.revokeObjectURL(preview); }, [preview]);

  async function analyze() {
    if (!file) return;
    setLoading("analysis"); setError("");
    try { setAnalysis(await uploadImage(file)); } catch (requestError) { setError(requestError.message); }
    finally { setLoading(""); }
  }
  async function estimate() {
    setLoading("price"); setError("");
    try { setPriceResult(await apiPost("/price/used-car", pricePayload(details))); } catch (requestError) { setError(requestError.message); }
    finally { setLoading(""); }
  }
  async function findSimilar() {
    setLoading("similar"); setError("");
    try {
      setSimilar(await apiPost("/image/similar-cars", {
        make: details.brand, model: details.model, year: Number(details.year),
        mileage_km: Number(details.mileage_km), fuel: details.fuel_type,
        transmission: details.transmission_type, listing_type: "used",
      }));
    } catch (requestError) { setError(requestError.message); }
    finally { setLoading(""); }
  }

  return (
    <section id="image-evaluation">
      <SectionHeader gear="AI" title="Image Evaluation" description="Run an image-assisted car evaluation" />
      <p className="section-copy">The image is used for safety, quality, and context. It does not identify an exact vehicle or predict price alone.</p>
      <div className="image-evaluation-grid">
        <div className="panel upload-panel">
          <Field label="Vehicle image"><input type="file" accept=".jpg,.jpeg,.png,.webp" onChange={(e) => { setFile(e.target.files?.[0]); setAnalysis(null); }} /></Field>
          {preview && <img className="preview" src={preview} alt="Uploaded vehicle preview" />}
          <LoadingButton loading={loading === "analysis"} disabled={!file} onClick={analyze}>Analyze image</LoadingButton>
        </div>
        {analysis && <div className="assistant-card"><span className="assistant-label">Image evaluation</span><h3>{analysis.message}</h3><p>Safety: {analysis.safe_image ? "Passed" : "Rejected"} · Accepted: {analysis.accepted_for_analysis ? "Yes" : "No"}</p><p>Quality: {analysis.quality_status || "Unavailable"} · Vehicle visibility: {analysis.vehicle_visibility_status || "Unavailable"}</p><p>Dominant color: {analysis.dominant_color || "Unknown"} · Estimated body type: {analysis.estimated_body_type || "Unknown"}</p>{analysis.warnings?.length > 0 && <Notice type="warning">{analysis.warnings.join(" · ")}</Notice>}<details><summary>Technical image analysis details</summary><pre>{JSON.stringify(analysis, null, 2)}</pre></details></div>}
      </div>
      {analysis?.accepted_for_analysis && <div className="panel confirm-panel"><h3>Continue with confirmed vehicle details</h3><p className="warning-text">AutoAdvisor does not estimate price from image alone. The image is used for safety/quality/context; the price estimate uses confirmed structured details.</p><PriceFields details={details} setDetails={setDetails} /><div className="button-row"><LoadingButton loading={loading === "price"} onClick={estimate}>Estimate fair price from confirmed details</LoadingButton><LoadingButton loading={loading === "similar"} className="secondary" onClick={findSimilar}>Find similar cars in inventory</LoadingButton></div><Notice error={error} /></div>}
      <PriceResult result={priceResult} details={details} />
      {similar && <><div className="assistant-card"><span className="assistant-label">Inventory match</span><p>Similar cars are matched from the AutoAdvisor inventory using confirmed details, not from image recognition alone.</p><p>{similar.explanation?.includes("Exact matches were limited") ? "Exact matches were limited, so these results include the closest available alternatives from the curated demo inventory." : "These are the closest available matches from the curated demo inventory."}</p></div><CarGrid cars={similar.similar_cars} /></>}
    </section>
  );
}

function DealerSection() {
  return (
    <section id="save">
      <SectionHeader gear="S" title="Save Interest / Dealer Draft" description="Save buyer interest and prepare a dealer inquiry draft" />
      <p className="section-copy">This saves a buyer interest draft. No email, WhatsApp, or dealer contact is sent automatically.</p>
      <div className="panel">
        <SaveInterestForm allowCarId initiallyOpen />
      </div>
    </section>
  );
}

export default function App() {
  const [backendOnline, setBackendOnline] = useState(null);
  useEffect(() => {
    apiGet("/health").then(() => setBackendOnline(true)).catch(() => setBackendOnline(false));
  }, []);

  return (
    <>
      <nav>
        <button className="brand" onClick={() => scrollTo("top")}><img src={logo} alt="AutoAdvisor AI" /><span>AutoAdvisor AI</span></button>
        <div className="nav-links">{gears.map(([letter, name, , id]) => <button key={id} onClick={() => scrollTo(id)}>{letter} · {name}</button>)}</div>
        <span className={`status ${backendOnline ? "online" : backendOnline === false ? "offline" : ""}`}>{backendOnline ? "Backend online" : backendOnline === false ? "Backend offline" : "Checking backend"}</span>
      </nav>
      <main>
        <header id="top" className="hero">
          <div className="hero-copy"><p className="eyebrow">Lebanon / MENA car-buying intelligence</p><h1>AutoAdvisor AI</h1><h2>Smart Advice. Better Drives.</h2><p>AI-powered car discovery, fair-price evaluation, image-assisted inspection, and dealer inquiry drafts for Lebanon/MENA.</p><div className="button-row"><button onClick={() => scrollTo("drive")}>Start in Drive</button><button className="secondary" onClick={() => scrollTo("park")}>Explore Inventory</button></div><div className="trust-row">{["120-car curated demo inventory", "Optional OpenAI response layer", "No live scraping", "Dealer messages are drafts only"].map((item) => <span key={item}>{item}</span>)}</div></div>
          <div className="hero-visual"><div className="shifter"><span>P</span><span>R</span><span>N</span><strong>D</strong><span>S</span></div><div className="glow" /></div>
        </header>
        <section className="gear-selector"><p className="eyebrow">Choose your drive mode</p><div className="gear-track">{gears.map(([letter, name, description, id]) => <button className={letter === "D" ? "active" : ""} key={id} onClick={() => scrollTo(id)}><span>{letter}</span><strong>{name}</strong><small>{description}</small></button>)}</div></section>
        <DriveSection /><ParkSection /><NeutralSection /><ReverseSection /><ImageEvaluationSection /><DealerSection />
      </main>
      <footer><img src={logo} alt="" /><p>AutoAdvisor AI · Curated demo inventory · Backend: {BACKEND_LABEL}</p></footer>
    </>
  );
}
