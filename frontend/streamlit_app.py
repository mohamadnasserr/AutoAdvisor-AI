from datetime import date
from typing import Any

import requests
import streamlit as st


DEFAULT_API_BASE_URL = "http://127.0.0.1:8000"
REQUEST_TIMEOUT_SECONDS = 30


def normalize_base_url(base_url: str) -> str:
    return base_url.strip().rstrip("/") or DEFAULT_API_BASE_URL


def api_get(base_url: str, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    response = requests.get(
        f"{normalize_base_url(base_url)}{path}",
        params=params,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    return parse_response(response)


def api_post(base_url: str, path: str, payload: dict[str, Any]) -> dict[str, Any]:
    response = requests.post(
        f"{normalize_base_url(base_url)}{path}",
        json=payload,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    return parse_response(response)


def api_post_file(
    base_url: str,
    path: str,
    filename: str,
    content_type: str,
    file_bytes: bytes,
) -> dict[str, Any]:
    response = requests.post(
        f"{normalize_base_url(base_url)}{path}",
        files={"file": (filename, file_bytes, content_type)},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    return parse_response(response)


def parse_response(response: requests.Response) -> dict[str, Any]:
    try:
        data = response.json()
    except ValueError as exc:
        raise requests.RequestException(
            f"Backend returned a non-JSON response ({response.status_code})."
        ) from exc

    if not response.ok:
        detail = data.get("detail", data) if isinstance(data, dict) else data
        raise requests.RequestException(f"Backend error {response.status_code}: {detail}")

    return data


def compact_params(**values: Any) -> dict[str, Any]:
    return {
        key: value
        for key, value in values.items()
        if value is not None and value != "" and value != "Any"
    }


def show_request_error(exc: requests.RequestException) -> None:
    st.error(f"Could not complete the request: {exc}")


def display_car_table(cars: list[dict[str, Any]]) -> None:
    if not cars:
        return

    preferred_columns = [
        "id",
        "listing_type",
        "make",
        "model",
        "trim",
        "year",
        "price_usd",
        "mileage_km",
        "body_type",
        "fuel",
        "transmission",
        "region",
        "availability_status",
        "platform_source",
    ]
    available_columns = [
        key for key in preferred_columns if any(key in car for car in cars)
    ]
    rows = [{key: car.get(key) for key in available_columns} for car in cars]
    st.dataframe(rows, use_container_width=True, hide_index=True)


def display_recommendation_cards(cars: list[dict[str, Any]]) -> None:
    if not cars:
        return

    st.caption(
        "Recommended cars may include near-budget or nearby-region alternatives "
        "when exact matches are limited."
    )
    st.markdown("**Recommended cars**")

    for row_start in range(0, len(cars), 2):
        card_columns = st.columns(2)

        for column, car in zip(card_columns, cars[row_start : row_start + 2]):
            with column:
                with st.container(border=True):
                    trim = f" {car['trim']}" if car.get("trim") else ""
                    st.markdown(
                        f"#### {car.get('year', '')} {car.get('make', '')} "
                        f"{car.get('model', '')}{trim}"
                    )

                    price = car.get("price_usd")
                    mileage = car.get("mileage_km")
                    price_text = (
                        f"${price:,.0f}" if isinstance(price, (int, float)) else "Not listed"
                    )
                    mileage_text = (
                        f"{mileage:,} km"
                        if isinstance(mileage, (int, float))
                        else "Not listed"
                    )

                    headline = st.columns(2)
                    headline[0].metric("Price", price_text)
                    headline[1].metric("Mileage", mileage_text)

                    st.write(f"**Region:** {car.get('region') or 'Not listed'}")
                    st.write(
                        "**Details:** "
                        f"{car.get('body_type') or 'Unknown body type'} | "
                        f"{car.get('fuel') or 'Unknown fuel'} | "
                        f"{car.get('transmission') or 'Unknown transmission'}"
                    )
                    st.caption(
                        f"Listing: {car.get('listing_type') or 'unknown'} | "
                        f"Availability: {car.get('availability_status') or 'unknown'}"
                    )


def normalize_inventory_response(result: Any) -> tuple[list[dict[str, Any]], int]:
    if isinstance(result, list):
        return result, len(result)

    if isinstance(result, dict):
        cars = result.get("results", [])
        if not isinstance(cars, list):
            cars = []
        count = result.get("count", len(cars))
        return cars, count if isinstance(count, int) else len(cars)

    return [], 0


def display_inventory_results(result: Any) -> None:
    cars, count = normalize_inventory_response(result)
    st.success(f"Found {count} cars.")

    if count == 0 or not cars:
        st.warning("No cars matched these filters. Try removing one or more filters.")
        return

    display_car_table(cars)


st.set_page_config(page_title="AutoAdvisor AI", layout="wide")

with st.sidebar:
    st.header("Backend")
    api_base_url = st.text_input("API base URL", value=DEFAULT_API_BASE_URL)

    if st.button("Check connection", use_container_width=True):
        try:
            health = api_get(api_base_url, "/health")
            st.success(f"Connected: {health.get('app', 'AutoAdvisor AI')}")
        except requests.RequestException as exc:
            show_request_error(exc)

    st.divider()
    st.info("Demo inventory and AI outputs should be verified before purchase.")

st.title("AutoAdvisor AI")
st.caption(
    "A Lebanon/MENA car-buying assistant with AI recommendations, used-car "
    "price checks, image safety and quality analysis, and dealer inquiry drafts."
)

(
    inventory_tab,
    chat_tab,
    compare_tab,
    price_tab,
    image_tab,
    dealer_tab,
) = st.tabs(
    [
        "Inventory Search",
        "AI Chat",
        "Compare Cars",
        "Used-Car Price Check",
        "Image Analysis",
        "Dealer Inquiry",
    ]
)

with inventory_tab:
    st.subheader("Search New and Used Inventory")
    st.info(
        "Searches the seeded AutoAdvisor inventory stored in PostgreSQL through "
        "the FastAPI backend."
    )

    with st.form("inventory_search_form"):
        row_one = st.columns(4)
        listing_type = row_one[0].selectbox(
            "Listing type", ["Any", "used", "new"], index=0
        )
        use_budget_filter = row_one[1].checkbox("Use budget filter", value=False)
        make = row_one[2].text_input("Make")
        body_type = row_one[3].selectbox(
            "Body type",
            ["Any", "Sedan", "SUV", "Hatchback", "Coupe", "Pickup", "Van"],
            index=0,
        )

        row_two = st.columns(4)
        budget_max = row_two[0].number_input(
            "Maximum budget (USD)",
            min_value=0.0,
            value=10000.0,
            step=500.0,
            disabled=not use_budget_filter,
        )
        fuel = row_two[1].selectbox(
            "Fuel", ["Any", "Petrol", "Diesel", "Hybrid", "Electric"], index=0
        )
        transmission = row_two[2].selectbox(
            "Transmission", ["Any", "Automatic", "Manual"], index=0
        )
        region = row_two[3].text_input("Region", value="")

        search_inventory = st.form_submit_button("Search inventory", type="primary")

    show_all_inventory = st.button("Show all inventory")

    if search_inventory:
        params = compact_params(
            listing_type=listing_type,
            budget_max=budget_max if use_budget_filter else None,
            make=make.strip(),
            body_type=body_type,
            fuel=fuel,
            transmission=transmission,
            region=region.strip(),
        )
        try:
            result = api_get(api_base_url, "/search/cars", params=params)
            display_inventory_results(result)
        except requests.RequestException as exc:
            show_request_error(exc)

    if show_all_inventory:
        try:
            result = api_get(api_base_url, "/cars")
            display_inventory_results(result)
        except requests.RequestException as exc:
            show_request_error(exc)

with chat_tab:
    st.subheader("Ask AutoAdvisor AI")

    if "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = []

    chat_controls = st.columns([4, 1])
    session_id = chat_controls[0].text_input(
        "Session ID",
        value="demo-session",
        key="ai_chat_session_id",
        help="Messages sent to the backend use this temporary chat-memory session.",
    )
    if chat_controls[1].button("Clear chat", use_container_width=True):
        st.session_state["chat_messages"] = []
        st.rerun()

    st.markdown("**Try an example prompt**")
    example_prompts = [
        "Reliable used car under $10,000 in Beirut",
        "Compare Toyota Corolla and Kia Picanto",
        "Is a 2018 Hyundai Tucson with 90,000 km for $14,000 fair?",
        "Connect me with the dealer for a Toyota Corolla",
    ]
    example_columns = st.columns(2)
    selected_prompt = None
    for index, prompt in enumerate(example_prompts):
        if example_columns[index % 2].button(
            prompt,
            key=f"chat_example_{index}",
            use_container_width=True,
        ):
            selected_prompt = prompt

    st.divider()

    for message in st.session_state["chat_messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message["role"] == "assistant" and message.get("debug"):
                debug = message["debug"]
                recommended_cars = debug.get("recommended_cars", [])
                display_recommendation_cards(recommended_cars)

                with st.expander("Debug details"):
                    st.write(f"**Intent:** {debug.get('intent', 'unknown')}")
                    st.markdown("**Extracted preferences**")
                    st.json(debug.get("extracted_preferences", {}))

                    if recommended_cars:
                        st.markdown("**Raw recommended cars**")
                        st.json(recommended_cars)
                    else:
                        st.info("No recommended cars returned for this response.")

    chat_input_message = st.chat_input(
        "Ask about recommendations, comparisons, prices, or dealers..."
    )
    user_message = selected_prompt or chat_input_message

    if user_message:
        st.session_state["chat_messages"].append(
            {"role": "user", "content": user_message}
        )
        with st.chat_message("user"):
            st.markdown(user_message)

        try:
            result = api_post(
                api_base_url,
                "/chat",
                {"message": user_message, "session_id": session_id or "demo-session"},
            )
            assistant_answer = result.get("answer", "No answer returned.")
            assistant_message = {
                "role": "assistant",
                "content": assistant_answer,
                "debug": {
                    "intent": result.get("intent", "unknown"),
                    "extracted_preferences": result.get("extracted_preferences", {}),
                    "recommended_cars": result.get("recommended_cars", []),
                },
            }
            st.session_state["chat_messages"].append(assistant_message)

            with st.chat_message("assistant"):
                st.markdown(assistant_answer)
                recommended_cars = assistant_message["debug"]["recommended_cars"]
                display_recommendation_cards(recommended_cars)

                with st.expander("Debug details"):
                    st.write(f"**Intent:** {assistant_message['debug']['intent']}")
                    st.markdown("**Extracted preferences**")
                    st.json(assistant_message["debug"]["extracted_preferences"])

                    if recommended_cars:
                        st.markdown("**Raw recommended cars**")
                        st.json(recommended_cars)
                    else:
                        st.info("No recommended cars returned for this response.")
        except requests.RequestException as exc:
            show_request_error(exc)

with compare_tab:
    st.subheader("Compare 2 to 5 Inventory Cars")

    with st.form("comparison_form"):
        raw_car_ids = st.text_input(
            "Car IDs",
            placeholder="Example: 1, 3, 7",
            help="Enter between 2 and 5 comma-separated inventory car IDs.",
        )
        compare_cars = st.form_submit_button("Compare cars", type="primary")

    if compare_cars:
        try:
            car_ids = [int(value.strip()) for value in raw_car_ids.split(",") if value.strip()]
            if not 2 <= len(car_ids) <= 5:
                st.warning("Please enter between 2 and 5 car IDs.")
            else:
                payload = {"car_ids": car_ids}
                try:
                    result = api_post(api_base_url, "/compare/cars", payload)
                except requests.RequestException as exc:
                    if "404" not in str(exc):
                        raise
                    result = api_post(api_base_url, "/compare", payload)

                st.success(f"Compared {result.get('compared_count', len(car_ids))} cars.")
                st.info(result.get("final_verdict", "No final verdict returned."))

                for car in result.get("cars", []):
                    title = car.get("title", f"Car #{car.get('id', '?')}")
                    with st.expander(title, expanded=True):
                        details, strengths, risks = st.columns(3)
                        with details:
                            st.markdown("**Details**")
                            st.write(f"Listing type: {car.get('listing_type', '-')}")
                            st.write(f"Price: ${car.get('price_usd', 0):,.0f}")
                            st.write(f"Year: {car.get('year', '-')}")
                            st.write(f"Mileage: {car.get('mileage_km', '-')}")
                            st.write(f"Best use case: {car.get('best_use_case', '-')}")
                        with strengths:
                            st.markdown("**Strengths**")
                            for item in car.get("strengths", []) or ["No strengths listed."]:
                                st.write(f"- {item}")
                        with risks:
                            st.markdown("**Risks**")
                            for item in car.get("risks", []) or ["No risks listed."]:
                                st.write(f"- {item}")
        except ValueError:
            st.error("Car IDs must be whole numbers separated by commas.")
        except requests.RequestException as exc:
            show_request_error(exc)

with price_tab:
    st.subheader("Estimate a Used-Car Fair Price Range")
    st.info("This model estimates used-car prices only and does not guarantee market value.")

    with st.form("price_check_form"):
        identity = st.columns(3)
        brand = identity[0].text_input("Brand", value="Hyundai")
        model = identity[1].text_input("Model", value="i20")
        year = identity[2].number_input(
            "Year", min_value=1990, max_value=date.today().year, value=2018
        )

        usage = st.columns(3)
        mileage_km = usage[0].number_input(
            "Mileage (km)", min_value=0, value=60000, step=1000
        )
        fuel_type = usage[1].selectbox(
            "Fuel type", ["Petrol", "Diesel", "CNG", "LPG", "Electric"]
        )
        transmission_type = usage[2].selectbox(
            "Transmission type", ["Manual", "Automatic"]
        )

        specifications = st.columns(4)
        vehicle_age = specifications[0].number_input(
            "Vehicle age", min_value=0, value=max(date.today().year - int(year), 0)
        )
        engine = specifications[1].number_input(
            "Engine (cc)", min_value=100.0, value=1200.0, step=100.0
        )
        mileage = specifications[2].number_input(
            "Fuel economy", min_value=0.1, value=18.0, step=0.5
        )
        max_power = specifications[3].number_input(
            "Max power", min_value=1.0, value=82.0, step=1.0
        )
        seats = st.number_input("Seats", min_value=1, max_value=20, value=5)

        estimate_price = st.form_submit_button("Estimate used-car price", type="primary")

    if estimate_price:
        payload = {
            "brand": brand,
            "model": model,
            "vehicle_age": int(vehicle_age),
            "km_driven": int(mileage_km),
            "fuel_type": fuel_type,
            "transmission_type": transmission_type,
            "mileage": float(mileage),
            "engine": float(engine),
            "max_power": float(max_power),
            "seats": int(seats),
        }
        try:
            result = api_post(api_base_url, "/price/used-car", payload)
            estimated = result.get("estimated_price_usd", 0)
            low = result.get("fair_price_low_usd", result.get("low_estimate_usd", 0))
            high = result.get("fair_price_high_usd", result.get("high_estimate_usd", 0))
            confidence = result.get("confidence", result.get("model_r2"))

            metrics = st.columns(4)
            metrics[0].metric("Estimated price", f"${estimated:,.0f}")
            metrics[1].metric("Fair price low", f"${low:,.0f}")
            metrics[2].metric("Fair price high", f"${high:,.0f}")
            metrics[3].metric(
                "Confidence",
                f"{confidence:.3f}" if isinstance(confidence, (int, float)) else "Not provided",
            )
            st.warning(result.get("disclaimer", "Verify this estimate against the local market."))
        except requests.RequestException as exc:
            show_request_error(exc)

with image_tab:
    st.subheader("Analyze Vehicle Image Safety and Quality")
    uploaded_file = st.file_uploader(
        "Upload a vehicle image",
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=False,
    )

    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        st.image(file_bytes, caption=uploaded_file.name, use_container_width=True)

        if st.button("Analyze image", type="primary"):
            try:
                result = api_post_file(
                    api_base_url,
                    "/image/analyze",
                    uploaded_file.name,
                    uploaded_file.type or "application/octet-stream",
                    file_bytes,
                )

                if result.get("safe_image") and result.get("accepted_for_analysis"):
                    st.success(result.get("message", "Image accepted for analysis."))
                elif result.get("safe_image"):
                    st.warning(result.get("message", "Image needs review."))
                else:
                    st.error(result.get("message", "Image rejected by safety checks."))

                status_fields = {
                    "safe_image": result.get("safe_image"),
                    "accepted_for_analysis": result.get("accepted_for_analysis"),
                    "nsfw_score": result.get("nsfw_score"),
                    "quality_status": result.get("quality_status"),
                    "blur_score": result.get("blur_score"),
                    "brightness_score": result.get("brightness_score"),
                    "edge_density": result.get("edge_density"),
                    "vehicle_visibility_status": result.get("vehicle_visibility_status"),
                    "dominant_color": result.get("dominant_color"),
                    "estimated_body_type": result.get("estimated_body_type"),
                    "analysis_status": result.get("analysis_status"),
                    "warnings": result.get("warnings", []),
                    "width": result.get("width"),
                    "height": result.get("height"),
                    "message": result.get("message"),
                }
                st.json(status_fields)
            except requests.RequestException as exc:
                show_request_error(exc)

with dealer_tab:
    st.subheader("Create a Safe Dealer Inquiry Draft")
    st.info("This creates a draft/demo lead only. No message is sent automatically.")

    with st.form("dealer_inquiry_form"):
        dealer_fields = st.columns(2)
        selected_car_id = dealer_fields[0].number_input(
            "Selected car ID", min_value=1, value=1, step=1
        )
        user_location = dealer_fields[1].text_input("Your location", value="Lebanon")

        contact_fields = st.columns(2)
        preferred_contact_method = contact_fields[0].selectbox(
            "Preferred contact method", ["phone", "email", "WhatsApp"]
        )
        budget = contact_fields[1].number_input(
            "Budget (USD)", min_value=0.0, value=0.0, step=500.0
        )
        create_inquiry = st.form_submit_button("Create inquiry draft", type="primary")

    if create_inquiry:
        payload = {
            "selected_car_id": int(selected_car_id),
            "user_location": user_location or None,
            "preferred_contact_method": preferred_contact_method,
            "budget": budget if budget > 0 else None,
        }
        try:
            result = api_post(api_base_url, "/dealer/leads", payload)
            st.success(f"Draft lead created with status: {result.get('status', 'draft')}")

            dealer_details = st.columns(2)
            with dealer_details[0]:
                st.markdown("**Dealership**")
                st.write(f"Name: {result.get('dealership_name') or 'Not available'}")
                st.write(f"Location: {result.get('dealership_location') or 'Not available'}")
            with dealer_details[1]:
                st.markdown("**Contact details**")
                st.write(f"Phone: {result.get('dealership_phone') or 'Not available'}")
                st.write(f"Email: {result.get('dealership_email') or 'Not available'}")

            st.markdown("**Inquiry draft**")
            st.code(result.get("message_draft", "No draft returned."), language=None)
            st.warning("No email, WhatsApp message, or dealer contact was sent automatically.")
        except requests.RequestException as exc:
            show_request_error(exc)
