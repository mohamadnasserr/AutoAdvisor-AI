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
  { letter: "P", name: "Park", label: "Browse Inventory", id: "park" },
  { letter: "R", name: "Rate", label: "Fair Price Check", id: "reverse" },
  { letter: "N", name: "Neutral", label: "Compare Cars", id: "neutral" },
  { letter: "D", name: "Drive", label: "Ask AutoAdvisor AI", id: "drive" },
  { letter: "S", name: "Save", label: "Save Interest / Dealer Draft", id: "save" },
];

const defaultPriceDetails = {
  brand: "Toyota",
  model: "Yaris",
  year: 2018,
  mileage_km: 60000,
  body_type: "Hatchback",
  fuel_type: "Petrol",
  transmission_type: "Automatic",
  vehicle_age: 8,
  engine: 1200,
  mileage: 18,
  max_power: 82,
  seats: 5,
  budget_max: "",
  condition: "Good",
};

const emptyConfirmedVehicleDetails = {
  brand: "",
  model: "",
  year: "",
  mileage_km: "",
  body_type: "",
  fuel_type: "Petrol",
  transmission_type: "Automatic",
  vehicle_age: "",
  engine: "",
  mileage: "",
  max_power: "",
  seats: "",
  budget_max: "",
  condition: "Good",
};

function scrollTo(id) {
  document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
}

function GearboxSelector({ activeGear, onSelectGear, floating = false }) {
  const activeGearIndex = Math.max(
    0,
    gears.findIndex((gear) => gear.letter === activeGear),
  );

  return (
    <div
      className={`gearbox-shell ${floating ? "floating" : ""}`}
      style={{
        "--gear-y": `${activeGearIndex * 61.68}px`,
        "--gear-y-floating": `${activeGearIndex * 47.6}px`,
        "--gear-path": `${activeGearIndex * 61.68 + 28}px`,
        "--gear-path-floating": `${activeGearIndex * 47.6 + 22}px`,
      }}
      aria-label="PRNDS navigation selector"
    >
      <div className="gearbox-plate">
        <div className="gearbox-slot" />
        <div className="gearbox-gate" />
        <div className="gearbox-active-path" aria-hidden="true" />
        <div className="gearbox-label">PRNDS</div>
        <div className="gearbox-options">
          <span className="gearbox-knob" aria-hidden="true" />
          {gears.map((gear) => (
            <button
              key={gear.letter}
              className={activeGear === gear.letter ? "active" : ""}
              onClick={() => onSelectGear(gear)}
              aria-label={`${gear.letter} ${gear.name}: ${gear.label}`}
            >
              <span className="gear-letter">{gear.letter}</span>
              <span className="gear-text">
                <strong>{gear.name}</strong>
                <small>{gear.label}</small>
              </span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
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

function titleCase(value) {
  if (!value) return "Unknown";
  return String(value)
    .replace(/_/g, " ")
    .split(" ")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(" ");
}

function carDisplayName(car) {
  const year = car.year || "";
  const make = car.make || car.brand || "";
  const model = car.model || "";
  const title = car.title || `${year} ${make} ${model}`;
  return title.trim().replace(/\s+/g, " ") || "This car";
}

function includesAny(value, terms) {
  return terms.some((term) => value.includes(term));
}

function addSentence(sentences, sentence) {
  if (sentence && !sentences.includes(sentence)) sentences.push(sentence);
}

function addTag(tags, tag) {
  if (tag) tags.add(tag);
}

function buildAdvisorOverview(car) {
  const bodyType = String(car.body_type || "").toLowerCase();
  const fuel = String(car.fuel || car.fuel_type || "").toLowerCase();
  const transmission = String(car.transmission || car.transmission_type || "").toLowerCase();
  const listingType = String(car.listing_type || "").toLowerCase();
  const status = String(car.availability_status || "").toLowerCase();
  const make = String(car.make || car.brand || "");
  const makeLower = make.toLowerCase();
  const model = String(car.model || "");
  const modelLower = model.toLowerCase();
  const year = Number(car.year);
  const mileage = car.mileage_km === null || car.mileage_km === undefined
    ? Number.NaN
    : Number(car.mileage_km);
  const price = Number(car.price_usd || car.estimated_price_usd || 0);
  const name = carDisplayName(car);
  const sentences = [];
  const tags = new Set();
  const cityModels = ["yaris", "picanto", "i10"];
  const balancedSedans = ["corolla", "civic", "sunny", "sentra"];
  const familyCrossovers = ["tucson", "sportage", "x-trail", "x trail", "duster"];
  const largeSuvs = ["pajero", "grand cherokee", "wrangler"];
  const premiumModels = ["c-class", "c class", "3 series", "a3", "a4", "lexus"];
  const utilityModels = ["ranger"];
  const commonResaleMakes = ["toyota", "honda", "nissan", "hyundai", "kia", "lexus"];
  const premiumMakes = ["mercedes-benz", "mercedes", "bmw", "audi", "lexus"];

  if (includesAny(modelLower, cityModels)) {
    addSentence(sentences, `${name} has the profile of a compact city runabout, often a good fit for first-car buyers, daily commuting, and easy parking.`);
    addTag(tags, "City-friendly");
    addTag(tags, "Budget-friendly");
  } else if (includesAny(modelLower, balancedSedans)) {
    addSentence(sentences, `${name} sits in the practical sedan zone: useful for daily use, commuting, and buyers who want common parts and broad market familiarity.`);
    addTag(tags, "Strong resale appeal");
    addTag(tags, "Comfort-focused");
  } else if (includesAny(modelLower, familyCrossovers)) {
    addSentence(sentences, `${name} is the kind of crossover/SUV that may suit family use, mixed city/highway driving, and buyers who want more cabin space.`);
    addTag(tags, "Family-friendly");
    addTag(tags, "Comfort-focused");
  } else if (includesAny(modelLower, largeSuvs)) {
    addSentence(sentences, `${name} leans toward the larger-SUV side, with road presence and rough-road or outdoor appeal, but running costs are worth checking carefully.`);
    addTag(tags, "Family-friendly");
    addTag(tags, "Inspection recommended");
  } else if (includesAny(modelLower, premiumModels) || premiumMakes.includes(makeLower)) {
    addSentence(sentences, `${name} may appeal to buyers looking for a more premium cabin, stronger features, and a more refined feel, with a higher maintenance budget expected.`);
    addTag(tags, "Premium feel");
    addTag(tags, "Comfort-focused");
  } else if (includesAny(modelLower, utilityModels) || bodyType.includes("pickup") || bodyType.includes("van")) {
    addSentence(sentences, `${name} is more utility-focused, typically practical for cargo, work use, business needs, or heavier-duty daily tasks.`);
    addTag(tags, "Utility-focused");
  } else if (bodyType.includes("hatchback")) {
    addSentence(sentences, `${name} should be easy to live with in tight streets and short city trips, especially if running costs matter.`);
    addTag(tags, "City-friendly");
  } else if (bodyType.includes("sedan")) {
    addSentence(sentences, `${name} looks like a straightforward daily driver with a useful balance of comfort, practicality, and commuting value.`);
    addTag(tags, "Comfort-focused");
  } else if (bodyType.includes("suv")) {
    addSentence(sentences, `${name} may be a good fit if you want a higher seating position, extra space, and stronger road presence.`);
    addTag(tags, "Family-friendly");
  } else if (bodyType.includes("coupe")) {
    addSentence(sentences, `${name} may appeal more to style-focused drivers than buyers chasing maximum practicality.`);
    addTag(tags, "Premium feel");
  } else {
    addSentence(sentences, `${name} is worth comparing if its price, mileage, and condition line up with your use case.`);
  }

  if (Number.isFinite(year)) {
    if (year >= 2023) {
      addSentence(sentences, `Being a newer model, it may offer more modern features and warranty potential, depending on trim and seller terms.`);
      addTag(tags, "Newer model");
    } else if (year >= 2018) {
      addSentence(sentences, `The ${year} model year puts it in a modern used-car sweet spot for many buyers: newer feel without new-car pricing.`);
      addTag(tags, "Value range");
    } else {
      addSentence(sentences, `As an older model, it may be budget-friendly, but inspection quality and maintenance records become especially important.`);
      addTag(tags, "Budget-friendly");
      addTag(tags, "Inspection recommended");
    }
  }

  if (Number.isFinite(mileage) && listingType !== "new") {
    if (mileage < 30000) {
      addSentence(sentences, `Its low-mileage profile is appealing on paper, though condition and service records still need confirmation.`);
      addTag(tags, "Low mileage");
    } else if (mileage <= 90000) {
      addSentence(sentences, `The mileage is moderate for a used car, so it could be a sensible shortlist candidate if servicing checks out.`);
      addTag(tags, "Value range");
    } else {
      addSentence(sentences, `With higher mileage, a pre-purchase inspection and service-history review should be part of the decision.`);
      addTag(tags, "Inspection recommended");
    }
  } else if (listingType === "new") {
    addSentence(sentences, `As a new listing, it may be attractive for warranty coverage and lower short-term maintenance risk.`);
    addTag(tags, "Newer model");
  } else {
    addSentence(sentences, `Mileage should be confirmed before comparing it seriously with other options.`);
    addTag(tags, "Inspection recommended");
  }

  if (price > 0) {
    if (price <= 8000) {
      addSentence(sentences, `The price is budget-focused, which can be useful for cost control, but condition checks matter more at this level.`);
      addTag(tags, "Budget-friendly");
    } else if (price <= 15000) {
      addSentence(sentences, `It sits in a value used-car range where buyers often balance price, mileage, and long-term ownership costs.`);
      addTag(tags, "Value range");
    } else if (price <= 30000) {
      addSentence(sentences, `At this price point, expect stronger comfort, features, or newer-year appeal compared with entry-level options.`);
      addTag(tags, "Comfort-focused");
    } else {
      addSentence(sentences, `This is in the premium or newer segment, so compare features, warranty terms, and depreciation carefully.`);
      addTag(tags, "Premium feel");
    }
  }

  if (fuel.includes("hybrid") || fuel.includes("electric")) {
    addSentence(sentences, `The ${fuel.includes("electric") ? "electric" : "hybrid"} setup is efficiency-focused and may reduce fuel use, while battery condition or warranty is worth checking.`);
    addTag(tags, "Fuel-efficient");
  } else if (fuel.includes("diesel")) {
    addSentence(sentences, `Diesel may suit longer-distance driving thanks to torque and economy, but maintenance history should be reviewed carefully.`);
    addTag(tags, "Fuel-efficient");
    addTag(tags, "Inspection recommended");
  } else if (fuel.includes("petrol")) {
    addSentence(sentences, `The petrol setup is familiar for local ownership, with fuel economy depending on engine size, traffic, and driving style.`);
  }

  if (transmission.includes("automatic")) {
    addSentence(sentences, `Automatic transmission should make stop-and-go traffic and daily driving easier.`);
    addTag(tags, "Comfort-focused");
  } else if (transmission.includes("manual")) {
    addSentence(sentences, `Manual transmission may keep ownership simpler and purchase cost lower, though it is less convenient in heavy traffic.`);
    addTag(tags, "Budget-friendly");
  }

  if (commonResaleMakes.includes(makeLower)) {
    addSentence(sentences, `${make} often has broad buyer familiarity in the region, which may help resale appeal if the car is clean and priced sensibly.`);
    addTag(tags, "Strong resale appeal");
  }

  if (status === "sold") {
    addSentence(sentences, `It is marked sold, so use it mainly as a reference point and search for similar available alternatives.`);
  } else if (status === "reserved") {
    addSentence(sentences, `It is marked reserved, so availability should be checked before spending too much time on it.`);
  } else if (status === "available") {
    addSentence(sentences, `It is currently shown as available in the demo inventory, so it is reasonable to compare against nearby alternatives.`);
  }

  const sentenceOffset = Number.isFinite(year) ? year % 3 : modelLower.length % 3;
  const prioritizedSentences = [
    sentences[0],
    ...sentences.slice(1 + sentenceOffset),
    ...sentences.slice(1, 1 + sentenceOffset),
  ].filter(Boolean);

  return {
    tags: [...tags].slice(0, 4),
    sentences: prioritizedSentences.slice(0, 4),
  };
}

function AdvisorTags({ tags }) {
  if (!tags?.length) return null;

  return (
    <div className="advisor-tags">
      {tags.map((tag) => (
        <span key={tag}>{tag}</span>
      ))}
    </div>
  );
}

function uniqueSortedValues(cars, key) {
  return [...new Set(cars.map((car) => car[key]).filter(Boolean))].sort((a, b) =>
    String(a).localeCompare(String(b)),
  );
}

function compareKeyFor(item) {
  if (item.compareKey) return item.compareKey;
  if (item.kind === "uploaded_profile") return `uploaded-${item.profileKey}`;
  return `inventory-${item.id}`;
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

function CarCard({ car, compareSelection = [], onAddCompare }) {
  const status = String(car.availability_status || "unknown").toLowerCase();
  const isSold = status === "sold";
  const carCompareKey = compareKeyFor(car);
  const advisor = buildAdvisorOverview(car);
  const imageUrl = String(car.image_url || "").trim();
  const [imageUnavailable, setImageUnavailable] = useState(!imageUrl);
  useEffect(() => {
    setImageUnavailable(!imageUrl);
  }, [imageUrl]);
  const isSelectedForCompare = compareSelection.some(
    (item) => compareKeyFor(item) === carCompareKey,
  );
  const compareSelectionFull = compareSelection.length >= 5 && !isSelectedForCompare;

  return (
    <article className="car-card">
      {!imageUnavailable ? (
        <img
          src={imageUrl}
          alt={`Representative ${car.make} ${car.model}`}
          onError={() => setImageUnavailable(true)}
        />
      ) : (
        <div className="car-image-placeholder">
          <span>AutoAdvisor AI</span>
          <strong>Representative image unavailable</strong>
        </div>
      )}
      <div className="car-card-body">
        <div className="car-card-meta">
          <span>Car ID: {car.id}</span>
          <span>Listing: {titleCase(car.listing_type || "listing")}</span>
          <span className={`status-badge ${status}`}>Status: {titleCase(status)}</span>
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
        <AdvisorTags tags={advisor.tags} />
        <details className="advisor-overview">
          <summary>Advisor overview</summary>
          <div>
            {advisor.sentences.map((sentence) => (
              <p key={sentence}>{sentence}</p>
            ))}
          </div>
        </details>
        {isSold && (
          <p className="sold-interest-note">
            This car is marked sold. You can still save interest for similar alternatives.
          </p>
        )}
        {onAddCompare && (
          <button
            className="compare-card-button"
            disabled={isSelectedForCompare || compareSelectionFull}
            onClick={() => onAddCompare(car)}
          >
            {isSelectedForCompare
              ? "Added to Compare"
              : compareSelectionFull
                ? "Compare list full"
                : "Add to Compare"}
          </button>
        )}
        <SaveInterestForm carId={car.id} defaultBudget={car.price_usd || ""} />
      </div>
    </article>
  );
}

function CarGrid({
  cars,
  empty = "No cars to display.",
  compareSelection = [],
  onAddCompare,
  pageSize = 6,
}) {
  const [visibleCount, setVisibleCount] = useState(pageSize);
  useEffect(() => {
    setVisibleCount(pageSize);
  }, [cars, pageSize]);

  if (!cars?.length) return <p className="muted">{empty}</p>;

  const visibleCars = cars.slice(0, visibleCount);
  const canShowMore = visibleCount < cars.length;
  const canResetView = visibleCount > pageSize;

  return (
    <>
      <p className="representative-note">
        Images are representative demo visuals, not verified listing photos.
      </p>
      <div className="car-grid-controls">
        <span>
          Showing {Math.min(visibleCount, cars.length)} of {cars.length} cars
        </span>
        <div>
          {canShowMore && (
            <button
              className="secondary"
              onClick={() => setVisibleCount((count) => Math.min(count + pageSize, cars.length))}
            >
              Show more
            </button>
          )}
          {canResetView && (
            <button className="secondary" onClick={() => setVisibleCount(pageSize)}>
              Reset view
            </button>
          )}
        </div>
      </div>
      <div className="car-grid">
        {visibleCars.map((car) => (
          <CarCard
            key={car.id}
            car={car}
            compareSelection={compareSelection}
            onAddCompare={onAddCompare}
          />
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

function PriceFields({ details, setDetails, includeProfileFields = false }) {
  const update = (key, value) => setDetails((current) => ({ ...current, [key]: value }));
  return (
    <div className="form-grid">
      <Field label="Brand"><input value={details.brand} onChange={(e) => update("brand", e.target.value)} /></Field>
      <Field label="Model"><input value={details.model} onChange={(e) => update("model", e.target.value)} /></Field>
      <Field label="Year"><input type="number" value={details.year} onChange={(e) => update("year", e.target.value)} /></Field>
      <Field label="Mileage (km)"><input type="number" value={details.mileage_km} onChange={(e) => update("mileage_km", e.target.value)} /></Field>
      {includeProfileFields && (
        <Field label="Body type">
          <select value={details.body_type} onChange={(e) => update("body_type", e.target.value)}>
            {["", "Sedan", "SUV", "Hatchback", "Coupe", "Pickup", "Van"].map((item) => <option key={item} value={item}>{item || "Select body type"}</option>)}
          </select>
        </Field>
      )}
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
      {!includeProfileFields && (
        <Field label="Fuel economy"><input type="number" step="0.1" value={details.mileage} onChange={(e) => update("mileage", e.target.value)} /></Field>
      )}
      <Field label="Max power"><input type="number" value={details.max_power} onChange={(e) => update("max_power", e.target.value)} /></Field>
      <Field label="Seats"><input type="number" value={details.seats} onChange={(e) => update("seats", e.target.value)} /></Field>
      {includeProfileFields && (
        <>
          <Field label="Budget"><input type="number" value={details.budget_max} onChange={(e) => update("budget_max", e.target.value)} placeholder="Optional" /></Field>
          <Field label="Condition">
            <select value={details.condition} onChange={(e) => update("condition", e.target.value)}>
              {["Excellent", "Good", "Fair", "Needs inspection"].map((item) => <option key={item}>{item}</option>)}
            </select>
          </Field>
        </>
      )}
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
    mileage: Number(details.mileage || 18),
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
    </div>
  );
}

function DriveSection({ compareSelection, onAddCompare }) {
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
      <SectionHeader gear="D" title="Drive" description="Ask AutoAdvisor AI" />
      <p className="section-copy">Intent routing, inventory search, chat memory, recommendations, and optional OpenAI response polishing.</p>
      <div className="prompt-row">{examples.map((item) => <button className="prompt-chip" key={item} onClick={() => send(item)}>{item}</button>)}</div>
      <div className="chat-shell">
        <div className="chat-log">
          {messages.map((message, index) => (
            <div className={`message ${message.role}`} key={`${message.role}-${index}`}>
              <div className="message-bubble">{message.content}</div>
              {message.meta?.recommended_cars?.length > 0 && (
                <CarGrid
                  cars={message.meta.recommended_cars}
                  compareSelection={compareSelection}
                  onAddCompare={onAddCompare}
                />
              )}
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

function ParkSection({ compareSelection, onAddCompare }) {
  const [filters, setFilters] = useState({
    listing_type: "Any",
    budget_max: "",
    make: "Any make",
    body_type: "Any body type",
    fuel: "Any fuel",
    transmission: "Any transmission",
    region: "Any region",
    available_only: true,
  });
  const [allInventory, setAllInventory] = useState([]);
  const [cars, setCars] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const update = (key, value) => setFilters((current) => ({ ...current, [key]: value }));

  const makeOptions = ["Any make", ...uniqueSortedValues(allInventory, "make")];
  const bodyTypeOptions = ["Any body type", ...uniqueSortedValues(allInventory, "body_type")];
  const fuelOptions = ["Any fuel", ...uniqueSortedValues(allInventory, "fuel")];
  const transmissionOptions = [
    "Any transmission",
    ...uniqueSortedValues(allInventory, "transmission"),
  ];
  const regionOptions = ["Any region", ...uniqueSortedValues(allInventory, "region")];

  function availableFiltered(items) {
    if (!filters.available_only) return items;
    return items.filter((car) => car.availability_status === "available");
  }

  function inventoryResults(payload) {
    return Array.isArray(payload) ? payload : payload.results || [];
  }

  function searchParams() {
    return {
      listing_type: filters.listing_type === "Any" ? undefined : filters.listing_type,
      budget_max: filters.budget_max || undefined,
      make: filters.make === "Any make" ? undefined : filters.make,
      body_type: filters.body_type === "Any body type" ? undefined : filters.body_type,
      fuel: filters.fuel === "Any fuel" ? undefined : filters.fuel,
      transmission:
        filters.transmission === "Any transmission" ? undefined : filters.transmission,
      region: filters.region === "Any region" ? undefined : filters.region,
      availability_status: filters.available_only ? "available" : undefined,
    };
  }

  async function loadAllInventory(showResults = false) {
    setLoading(true); setError("");
    try {
      const result = await apiGet("/cars");
      const inventory = inventoryResults(result);
      setAllInventory(inventory);
      if (showResults) setCars(availableFiltered(inventory));
      if (!cars.length) setCars(availableFiltered(inventory));
    } catch (requestError) { setError(requestError.message); }
    finally { setLoading(false); }
  }

  useEffect(() => {
    loadAllInventory(true);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function searchInventory() {
    setLoading(true); setError("");
    try {
      const result = await apiGet("/search/cars", searchParams());
      setCars(availableFiltered(inventoryResults(result)));
    } catch (requestError) { setError(requestError.message); }
    finally { setLoading(false); }
  }

  return (
    <section id="park">
      <SectionHeader gear="P" title="Park" description="Browse Inventory" />
      <p className="section-copy">This is curated demo inventory, not live scraped marketplace data.</p>
      <div className="panel">
        <div className="form-grid compact">
          <Field label="Listing type"><select value={filters.listing_type} onChange={(e) => update("listing_type", e.target.value)}>{["Any", "used", "new"].map((v) => <option key={v}>{v}</option>)}</select></Field>
          <Field label="Budget max"><input type="number" value={filters.budget_max} onChange={(e) => update("budget_max", e.target.value)} placeholder="Optional" /></Field>
          <Field label="Make"><select value={filters.make} onChange={(e) => update("make", e.target.value)}>{makeOptions.map((v) => <option key={v}>{v}</option>)}</select></Field>
          <Field label="Body type"><select value={filters.body_type} onChange={(e) => update("body_type", e.target.value)}>{bodyTypeOptions.map((v) => <option key={v}>{v}</option>)}</select></Field>
          <Field label="Fuel"><select value={filters.fuel} onChange={(e) => update("fuel", e.target.value)}>{fuelOptions.map((v) => <option key={v}>{v}</option>)}</select></Field>
          <Field label="Transmission"><select value={filters.transmission} onChange={(e) => update("transmission", e.target.value)}>{transmissionOptions.map((v) => <option key={v}>{v}</option>)}</select></Field>
          <Field label="Region"><select value={filters.region} onChange={(e) => update("region", e.target.value)}>{regionOptions.map((v) => <option key={v}>{v}</option>)}</select></Field>
          <label className="checkbox-field">
            <input type="checkbox" checked={filters.available_only} onChange={(e) => update("available_only", e.target.checked)} />
            <span>Available only</span>
            <small>Turn off to include reserved and sold cars.</small>
          </label>
        </div>
        <div className="button-row">
          <LoadingButton loading={loading} onClick={searchInventory}>Search inventory</LoadingButton>
          <LoadingButton loading={loading} className="secondary" onClick={() => loadAllInventory(true)}>Show all inventory</LoadingButton>
        </div>
        <Notice error={error}>{cars.length ? `Showing ${cars.length} cars.` : ""}</Notice>
      </div>
      <CarGrid
        cars={cars}
        empty="Search or show all inventory to begin."
        compareSelection={compareSelection}
        onAddCompare={onAddCompare}
      />
    </section>
  );
}

function NeutralSection({ compareSelection, onRemoveCompare }) {
  const [ids, setIds] = useState("1, 2");
  const [result, setResult] = useState(null);
  const [selectedProfiles, setSelectedProfiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  useEffect(() => {
    setSelectedProfiles((current) =>
      current
        .map((profile) =>
          compareSelection.find((item) => compareKeyFor(item) === compareKeyFor(profile)),
        )
        .filter(Boolean),
    );
  }, [compareSelection]);

  async function compareSelected() {
    const inventoryCars = compareSelection.filter((item) => item.kind !== "uploaded_profile" && item.id);
    const uploadedProfiles = compareSelection.filter((item) => item.kind === "uploaded_profile");
    const carIds = inventoryCars.map((car) => car.id);

    if (compareSelection.length < 2) {
      setError("Select at least 2 cars to compare.");
      return;
    }
    setSelectedProfiles(uploadedProfiles);
    setNotice("");
    setError("");

    if (carIds.length < 2) {
      setResult(null);
      setNotice(
        "Inventory cars are compared through AutoAdvisor inventory. Uploaded profiles are displayed for side-by-side review.",
      );
      return;
    }

    setLoading(true);
    try {
      setResult(await compareCars(carIds));
      if (uploadedProfiles.length) {
        setNotice(
          "Inventory cars are compared through AutoAdvisor inventory. Uploaded profiles are displayed for side-by-side review.",
        );
      }
    } catch (requestError) { setError(`Could not compare selected cars: ${requestError.message}`); }
    finally { setLoading(false); }
  }
  async function submitManual() {
    const carIds = ids.split(",").map((id) => Number(id.trim())).filter(Number.isInteger);
    if (carIds.length < 2) {
      setError("Enter at least 2 car IDs to compare.");
      return;
    }
    setLoading(true); setError(""); setNotice(""); setSelectedProfiles([]);
    try { setResult(await compareCars(carIds)); } catch (requestError) { setError(`Could not compare those car IDs: ${requestError.message}`); }
    finally { setLoading(false); }
  }
  return (
    <section id="neutral">
      <SectionHeader gear="N" title="Neutral" description="Compare Cars" />
      <p className="section-copy">
        Compare cars selected from AI recommendations, inventory results, or image-assisted similar matches.
      </p>
      <div className="panel compare-selection-panel">
        <div className="compare-selection-header">
          <div>
            <h3>Selected for comparison</h3>
            <p className="muted">Choose 2 to 5 cars from any car card.</p>
          </div>
          <LoadingButton
            loading={loading}
            disabled={compareSelection.length < 2}
            onClick={compareSelected}
          >
            Compare selected cars
          </LoadingButton>
        </div>
        {compareSelection.length ? (
          <div className="compare-chip-row">
            {compareSelection.map((item) => {
              const advisor = buildAdvisorOverview(item);

              return (
                <div className={`compare-chip ${item.kind === "uploaded_profile" ? "profile" : ""}`} key={compareKeyFor(item)}>
                  <strong>{item.year || "Year"} {item.make || item.brand} {item.model}</strong>
                  <span>
                    {item.kind === "uploaded_profile"
                      ? "Confirmed image profile"
                      : `Car ID: ${item.id}`}
                  </span>
                  <AdvisorTags tags={advisor.tags.slice(0, 3)} />
                  <button onClick={() => onRemoveCompare(compareKeyFor(item))}>Remove</button>
                </div>
              );
            })}
          </div>
        ) : (
          <p className="muted">No cars selected yet.</p>
        )}
      </div>
      <div className="panel inline-panel">
        <Field label="Advanced: comma-separated car IDs"><input value={ids} onChange={(e) => setIds(e.target.value)} /></Field>
        <LoadingButton loading={loading} onClick={submitManual}>Compare manual IDs</LoadingButton>
      </div>
      <Notice error={error} />
      <Notice type="info">{notice}</Notice>
      {result && <>
        <div className="assistant-card"><span className="assistant-label">Verdict</span><p>{result.final_verdict}</p></div>
        <div className="comparison-grid">
          {result.cars.map((car) => {
            const advisor = buildAdvisorOverview(car);

            return (
              <article className="comparison-card" key={car.id}>
                <h3>{car.title}</h3>
                <p>${Number(car.price_usd).toLocaleString()} · {car.mileage_km?.toLocaleString() || 0} km</p>
                <p>{car.body_type} · {car.fuel} · {car.transmission}</p>
                <AdvisorTags tags={advisor.tags} />
                <details className="advisor-overview">
                  <summary>Advisor overview</summary>
                  <div>
                    {advisor.sentences.map((sentence) => (
                      <p key={sentence}>{sentence}</p>
                    ))}
                  </div>
                </details>
                <h4>Strengths</h4>
                <ul>{car.strengths.map((item) => <li key={item}>{item}</li>)}</ul>
                <h4>Risks</h4>
                <ul>{car.risks.map((item) => <li key={item}>{item}</li>)}</ul>
                <p><strong>Best use:</strong> {car.best_use_case}</p>
              </article>
            );
          })}
        </div>
      </>}
      {selectedProfiles.length > 0 && (
        <div className="uploaded-profile-block">
          <p className="section-copy">
            Uploaded profiles are user-confirmed details from image-assisted evaluation. They are not inventory listings.
          </p>
          <div className="comparison-grid">
            {selectedProfiles.map((profile) => (
              <article className="comparison-card uploaded-profile-card" key={compareKeyFor(profile)}>
                <span className="assistant-label">Uploaded profile</span>
                <h3>{profile.year || "Year"} {profile.make || "Make"} {profile.model || "Model"}</h3>
                <p>
                  {profile.mileage_km ? `${Number(profile.mileage_km).toLocaleString()} km` : "Mileage not confirmed"}
                </p>
                <p>{profile.body_type || "Body type not confirmed"} · {profile.fuel || "Fuel not confirmed"} · {profile.transmission || "Transmission not confirmed"}</p>
                {profile.condition && <p><strong>Condition:</strong> {profile.condition}</p>}
                {profile.estimated_price_usd && (
                  <p>
                    Estimated fair price: <strong>${Number(profile.estimated_price_usd).toLocaleString()}</strong>
                    {profile.low_estimate_usd && profile.high_estimate_usd
                      ? ` (${Number(profile.low_estimate_usd).toLocaleString()} to ${Number(profile.high_estimate_usd).toLocaleString()})`
                      : ""}
                  </p>
                )}
                <p className="muted">User-confirmed profile, not an inventory listing.</p>
              </article>
            ))}
          </div>
        </div>
      )}
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
      <SectionHeader gear="R" title="Rate" description="Fair Price Check" />
      <div className="panel"><PriceFields details={details} setDetails={setDetails} /><LoadingButton loading={loading} onClick={submit}>Estimate fair price</LoadingButton><Notice error={error} /></div>
      <PriceResult result={result} details={details} />
    </section>
  );
}

function ImageEvaluationSection({ compareSelection, onAddCompare }) {
  const [file, setFile] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [details, setDetails] = useState(emptyConfirmedVehicleDetails);
  const [priceResult, setPriceResult] = useState(null);
  const [similar, setSimilar] = useState(null);
  const [loading, setLoading] = useState("");
  const [error, setError] = useState("");
  const [profileNotice, setProfileNotice] = useState("");
  const preview = useMemo(() => file ? URL.createObjectURL(file) : "", [file]);
  useEffect(() => () => { if (preview) URL.revokeObjectURL(preview); }, [preview]);

  function resetConfirmedDetails() {
    setDetails(emptyConfirmedVehicleDetails);
    setPriceResult(null);
    setSimilar(null);
    setProfileNotice("");
  }

  function handleFileChange(event) {
    const nextFile = event.target.files?.[0] || null;
    setFile(nextFile);
    setAnalysis(null);
    setError("");
    resetConfirmedDetails();
  }

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
        mileage_km: Number(details.mileage_km), body_type: details.body_type,
        fuel: details.fuel_type, transmission: details.transmission_type,
        budget_max: details.budget_max ? Number(details.budget_max) : undefined,
        listing_type: "used",
      }));
    } catch (requestError) { setError(requestError.message); }
    finally { setLoading(""); }
  }
  function addUploadedProfileToCompare() {
    const profileKey = file
      ? `${file.name}-${file.size}-${file.lastModified}`
      : `manual-${Date.now()}`;
    const profile = {
      kind: "uploaded_profile",
      compareKey: `uploaded-${profileKey}`,
      profileKey,
      make: details.brand,
      model: details.model,
      year: details.year,
      mileage_km: details.mileage_km,
      body_type: details.body_type,
      fuel: details.fuel_type,
      transmission: details.transmission_type,
      budget_max: details.budget_max,
      condition: details.condition,
      estimated_price_usd: priceResult?.estimated_price_usd,
      low_estimate_usd: priceResult?.low_estimate_usd,
      high_estimate_usd: priceResult?.high_estimate_usd,
    };
    onAddCompare(profile);
    setProfileNotice("Confirmed image profile added to comparison.");
  }

  const uploadedProfileKey = file
    ? `uploaded-${file.name}-${file.size}-${file.lastModified}`
    : "";
  const uploadedProfileAlreadySelected = uploadedProfileKey
    ? compareSelection.some((item) => compareKeyFor(item) === uploadedProfileKey)
    : false;

  return (
    <section id="image-evaluation">
      <SectionHeader gear="AI" title="Image Evaluation" description="Run an image-assisted car evaluation" />
      <p className="section-copy">The image is used for safety, quality, and context. It does not identify an exact vehicle or predict price alone.</p>
      <div className="image-evaluation-grid">
        <div className="panel upload-panel">
          <Field label="Vehicle image"><input type="file" accept=".jpg,.jpeg,.png,.webp" onChange={handleFileChange} /></Field>
          {preview && <img className="preview" src={preview} alt="Uploaded vehicle preview" />}
          <LoadingButton loading={loading === "analysis"} disabled={!file} onClick={analyze}>Analyze image</LoadingButton>
        </div>
        {analysis && <div className="assistant-card"><span className="assistant-label">Image evaluation</span><h3>{analysis.message}</h3><p>Safety: {analysis.safe_image ? "Passed" : "Rejected"} · Accepted: {analysis.accepted_for_analysis ? "Yes" : "No"}</p><p>Quality: {analysis.quality_status || "Unavailable"} · Vehicle visibility: {analysis.vehicle_visibility_status || "Unavailable"}</p><p>Dominant color: {analysis.dominant_color || "Unknown"} · Estimated body type: {analysis.estimated_body_type || "Unknown"}</p>{analysis.warnings?.length > 0 && <Notice type="warning">{analysis.warnings.join(" · ")}</Notice>}</div>}
      </div>
      {analysis?.accepted_for_analysis && <div className="panel confirm-panel"><h3>Continue with confirmed vehicle details</h3><p className="warning-text">AutoAdvisor does not identify exact make/model from image alone. Please confirm the vehicle details.</p><p className="warning-text">AutoAdvisor does not estimate price from image alone. The image is used for safety/quality/context; the price estimate uses confirmed structured details.</p><PriceFields details={details} setDetails={setDetails} includeProfileFields /><div className="button-row"><button className="secondary" onClick={resetConfirmedDetails}>Clear confirmed details</button><LoadingButton loading={loading === "price"} onClick={estimate}>Estimate fair price from confirmed details</LoadingButton><LoadingButton loading={loading === "similar"} className="secondary" onClick={findSimilar}>Find similar cars in inventory</LoadingButton><button onClick={addUploadedProfileToCompare}>{uploadedProfileAlreadySelected ? "Update uploaded profile in compare" : "Add uploaded car profile to compare"}</button></div><Notice type="info">{profileNotice}</Notice><Notice error={error} /></div>}
      <PriceResult result={priceResult} details={details} />
      {similar && <><div className="assistant-card"><span className="assistant-label">Inventory match</span><p>Similar cars are matched from the AutoAdvisor inventory using confirmed details, not from image recognition alone.</p><p>{similar.explanation?.includes("Exact matches were limited") ? "Exact matches were limited, so these results include the closest available alternatives from the curated demo inventory." : "These are the closest available matches from the curated demo inventory."}</p></div><CarGrid cars={similar.similar_cars} compareSelection={compareSelection} onAddCompare={onAddCompare} /></>}
    </section>
  );
}

function DealerSection() {
  return (
    <section id="save">
      <SectionHeader gear="S" title="Save" description="Save Interest / Dealer Draft" />
      <p className="section-copy">This saves a buyer interest draft. No email, WhatsApp, or dealer contact is sent automatically.</p>
      <div className="panel">
        <SaveInterestForm allowCarId initiallyOpen />
      </div>
    </section>
  );
}

export default function App() {
  const [backendOnline, setBackendOnline] = useState(null);
  const [compareSelection, setCompareSelection] = useState([]);
  const [activeGear, setActiveGear] = useState("D");

  useEffect(() => {
    apiGet("/health").then(() => setBackendOnline(true)).catch(() => setBackendOnline(false));
  }, []);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        const visibleEntries = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio);

        if (visibleEntries[0]) {
          const matchingGear = gears.find((gear) => gear.id === visibleEntries[0].target.id);
          if (matchingGear) setActiveGear(matchingGear.letter);
        }
      },
      {
        rootMargin: "-35% 0px -45% 0px",
        threshold: [0.12, 0.3, 0.55],
      },
    );

    gears.forEach((gear) => {
      const section = document.getElementById(gear.id);
      if (section) observer.observe(section);
    });

    return () => observer.disconnect();
  }, []);

  function selectGear(gear) {
    setActiveGear(gear.letter);
    scrollTo(gear.id);
  }

  function addToCompare(car) {
    setCompareSelection((current) => {
      const nextKey = compareKeyFor(car);
      const existingIndex = current.findIndex((item) => compareKeyFor(item) === nextKey);

      if (existingIndex >= 0 && car.kind === "uploaded_profile") {
        return current.map((item, index) => (index === existingIndex ? car : item));
      }

      if (existingIndex >= 0 || current.length >= 5) {
        return current;
      }
      return [...current, car];
    });
  }

  function removeFromCompare(compareKey) {
    setCompareSelection((current) => current.filter((car) => compareKeyFor(car) !== compareKey));
  }

  return (
    <>
      <nav>
        <button className="brand" onClick={() => scrollTo("top")}><img src={logo} alt="AutoAdvisor AI" /><span>AutoAdvisor AI</span></button>
        <span className={`status ${backendOnline ? "online" : backendOnline === false ? "offline" : ""}`}>{backendOnline ? "Backend online" : backendOnline === false ? "Backend offline" : "Checking backend"}</span>
      </nav>
      <GearboxSelector activeGear={activeGear} onSelectGear={selectGear} floating />
      <main>
        <header id="top" className="hero">
          <div className="hero-copy"><p className="eyebrow">Lebanon / MENA car-buying intelligence</p><h1>AutoAdvisor AI</h1><h2>Smart Advice. Better Drives.</h2><p>AI-powered car discovery, fair-price evaluation, image-assisted inspection, and dealer inquiry drafts for Lebanon/MENA.</p><div className="button-row"><button onClick={() => scrollTo("drive")}>Start in Drive</button><button className="secondary" onClick={() => scrollTo("park")}>Explore Inventory</button></div></div>
          <div className="hero-visual"><GearboxSelector activeGear={activeGear} onSelectGear={selectGear} /><div className="glow" /></div>
        </header>
        <DriveSection compareSelection={compareSelection} onAddCompare={addToCompare} />
        <ParkSection compareSelection={compareSelection} onAddCompare={addToCompare} />
        <NeutralSection compareSelection={compareSelection} onRemoveCompare={removeFromCompare} />
        <ReverseSection />
        <ImageEvaluationSection compareSelection={compareSelection} onAddCompare={addToCompare} />
        <DealerSection />
      </main>
      <footer><img src={logo} alt="" /><p>AutoAdvisor AI by Mohamad Nasser</p></footer>
    </>
  );
}
