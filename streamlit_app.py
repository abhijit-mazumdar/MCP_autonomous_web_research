import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="MCPAgent Web Research UI", layout="wide")
st.title("🧠 MCPAgent Autonomous Web Research")

# --- Health Check ---
st.sidebar.header("Server Health")
health = requests.get(f"{API_URL}/health").json()
status = health.get("status", "unknown")
if status == "ok":
    st.sidebar.success(f"Server status: {status}")
else:
    st.sidebar.error(f"Server status: {status}")

# --- Create Research Task ---
st.header("1. Create a Research Task")
with st.form("create_task_form"):
    query = st.text_input("Enter your research query:")
    submitted = st.form_submit_button("Submit Task")
    if submitted and query:
        resp = requests.post(f"{API_URL}/research", json={"query": query})
        if resp.status_code == 200:
            st.success("Task submitted!")
        else:
            st.error(f"Error: {resp.text}")

# --- List All Research Tasks ---
st.header("2. All Research Tasks")
if st.button("Refresh Task List"):
    st.session_state["tasks"] = requests.get(f"{API_URL}/research").json()
tasks = st.session_state.get("tasks", requests.get(f"{API_URL}/research").json())
if tasks:
    st.dataframe(tasks)
    st.subheader("Task Details")
    for t in tasks:
        with st.expander(f"Task #{t['id']}: {t['query']}"):
            st.markdown(f"**Status:** {t['status']}")
            st.markdown(f"**Timestamp:** {t['timestamp']}")
            st.markdown("**Result:**")
            st.code(t['result'] or "No result yet.", language="markdown")
else:
    st.info("No research tasks found.")

# --- Update Research Task ---
st.header("3. Update a Research Task")
if tasks:
    task_ids = [t["id"] for t in tasks]
    selected_id = st.selectbox("Select Task ID to Update", task_ids)
    new_status = st.text_input("New Status", value="completed")
    new_result = st.text_area("New Result", value="")
    if st.button("Update Task"):
        resp = requests.patch(f"{API_URL}/research/{selected_id}", json={"status": new_status, "result": new_result})
        if resp.status_code == 200:
            st.success("Task updated!")
            st.session_state["tasks"] = requests.get(f"{API_URL}/research").json()
        else:
            st.error(f"Error: {resp.text}")
else:
    st.info("No tasks to update.")

# --- Analyze Content ---
st.header("4. Analyze Content with Llama 3.2")
content = st.text_area("Paste content to analyze:")
if st.button("Analyze Content") and content:
    resp = requests.post(f"{API_URL}/analyze", json={"content": content})
    if resp.status_code == 200:
        st.subheader("Analysis Result:")
        st.write(resp.json().get("analysis", "No result."))
    else:
        st.error(f"Error: {resp.text}") 