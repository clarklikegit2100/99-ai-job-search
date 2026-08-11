const state = { token: "", applications: [], templates: [], selected: null, action: null };
const list = document.querySelector("#application-list");
const workspace = document.querySelector("#workspace");
const dialog = document.querySelector("#decision-dialog");
const form = document.querySelector("#decision-form");
const input = document.querySelector("#decision-input");
const toast = document.querySelector("#toast");

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function showToast(message, isError = false) {
  toast.textContent = message;
  toast.classList.toggle("error", isError);
  toast.classList.add("visible");
  window.setTimeout(() => toast.classList.remove("visible"), 3600);
}

async function api(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (options.method === "POST") {
    headers["Content-Type"] = "application/json";
    headers["X-Approval-Token"] = state.token;
  }
  const response = await fetch(path, { ...options, headers, cache: "no-store" });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Request failed");
  return data;
}

function statusClass(status) {
  return `status ${String(status).toLowerCase().replaceAll("_", "-")}`;
}

function renderList() {
  list.replaceChildren();
  if (!state.applications.length) {
    list.append(el("p", "subline", "No Phase 1 application packages yet."));
    return;
  }
  for (const item of state.applications) {
    const button = el("button", "application-card");
    button.type = "button";
    button.classList.toggle("active", state.selected === item.application_id);
    const row = el("div", "card-row");
    row.append(el("h3", "", item.company || "Unknown company"));
    row.append(el("span", statusClass(item.status), item.status.replaceAll("_", " ")));
    button.append(row, el("p", "", item.role || "Unknown role"), el("p", "", item.template || "No template"));
    button.addEventListener("click", () => loadDetail(item.application_id));
    list.append(button);
  }
}

function metric(label, value) {
  const box = el("div", "metric");
  box.append(el("span", "", label), el("strong", "", value || "—"));
  return box;
}

function renderDetail(item) {
  workspace.replaceChildren();
  const header = el("div", "review-header");
  const title = el("div");
  title.append(el("p", "eyebrow", "Application package"), el("h2", "", item.company), el("p", "subline", item.role));
  header.append(title, el("span", statusClass(item.status), item.status.replaceAll("_", " ")));
  workspace.append(header);

  const metrics = el("div", "metrics");
  metrics.append(
    metric("Template", item.template?.name || item.template?.id),
    metric("Artifacts", String((item.artifacts || []).length)),
    metric("Updated", item.updated_at ? new Date(item.updated_at).toLocaleString() : "—"),
  );
  workspace.append(metrics);

  workspace.append(el("h2", "section-title", "Generated artifacts"));
  const artifacts = el("div", "artifact-list");
  if (!(item.artifacts || []).length) artifacts.append(el("p", "subline", "Artifacts have not been staged for review yet."));
  for (const artifact of item.artifacts || []) {
    const row = el("div", "artifact");
    const copy = el("div");
    copy.append(el("strong", "", artifact.path), el("p", "", `SHA-256 ${artifact.sha256}`));
    const link = el("a", "", "Open");
    link.href = `/files/${encodeURIComponent(item.application_id)}/${artifact.path.split("/").map(encodeURIComponent).join("/")}`;
    link.target = "_blank";
    link.rel = "noopener";
    row.append(copy, link);
    artifacts.append(row);
  }
  workspace.append(artifacts);

  workspace.append(el("div", "guardrail", "Document approval confirms only the exact files and hashes shown here. It does not authorize uploading or submitting an application. Phase 2 has no submission capability."));

  const actions = el("div", "actions");
  const approve = el("button", "primary", "Approve documents");
  approve.type = "button";
  approve.disabled = item.status !== "AWAITING_DOCUMENT_APPROVAL";
  approve.addEventListener("click", () => openDecision("approve"));
  const revise = el("button", "secondary", "Request revision");
  revise.type = "button";
  revise.disabled = !["AWAITING_DOCUMENT_APPROVAL", "DOCUMENT_APPROVED"].includes(item.status);
  revise.addEventListener("click", () => openDecision("revision"));
  const reject = el("button", "danger", "Reject package");
  reject.type = "button";
  reject.disabled = item.status === "REJECTED";
  reject.addEventListener("click", () => openDecision("reject"));
  actions.append(approve, revise, reject);
  workspace.append(actions);
}

async function renderWizard() {
  try {
    await loadTemplates();
  } catch (error) {
    showToast(`Could not load templates: ${error.message}. Restart the local server.`, true);
  }
  state.selected = null;
  renderList();
  workspace.replaceChildren();
  const panel = el("div", "wizard");
  panel.append(
    el("p", "eyebrow", "Phase 1 · guided intake"),
    el("h2", "", "Start a tailored resume package"),
    el("p", "wizard-intro", "Add the job, choose the resume family yourself, and create a private workspace. The AI drafting workflow will use this record and stop again when the generated documents are ready for your review."),
  );
  const formNode = el("form", "wizard-grid");
  formNode.id = "new-application-form";

  function field(labelText, name, type = "text", full = false) {
    const wrap = el("div", `field${full ? " full" : ""}`);
    const labelNode = el("label", "", labelText);
    labelNode.htmlFor = `new-${name}`;
    const control = document.createElement(type === "textarea" ? "textarea" : "input");
    control.id = `new-${name}`;
    control.name = name;
    if (type !== "textarea") control.type = type;
    wrap.append(labelNode, control);
    return wrap;
  }

  formNode.append(field("Company", "company"), field("Role", "role"), field("Job posting URL", "posting_url", "url", true));
  const templateWrap = el("div", "field full");
  const templateLabel = el("label", "", "Resume template");
  templateLabel.htmlFor = "new-template";
  const select = document.createElement("select");
  select.id = "new-template";
  select.name = "template";
  select.required = true;
  select.append(new Option("Choose a template…", ""));
  const availableTemplates = state.templates.filter((item) => item.active && item.available);
  for (const template of availableTemplates) {
    select.append(new Option(`${template.name} · ${template.type.toUpperCase()}`, template.id));
  }
  if (!availableTemplates.length) {
    const unavailable = new Option("No templates loaded — restart the local server", "");
    unavailable.disabled = true;
    select.append(unavailable);
  }
  const note = el("p", "template-note", "Jian ModernCV is the preferred LaTeX style. Family A–H provide role-specific Word baselines. Historical wording is not automatically treated as an approved fact.");
  templateWrap.append(templateLabel, select, note);
  formNode.append(templateWrap, field("Full job description", "posting_text", "textarea", true));
  const actions = el("div", "wizard-actions field full");
  const create = el("button", "primary", "Create Phase 1 package");
  create.type = "submit";
  const cancel = el("button", "secondary", "Cancel");
  cancel.type = "button";
  cancel.addEventListener("click", () => {
    workspace.replaceChildren(el("div", "empty-state", "Select an application package or start a new one."));
  });
  actions.append(create, cancel);
  formNode.append(actions);
  formNode.addEventListener("submit", createApplication);
  panel.append(formNode);
  workspace.append(panel);
}

async function createApplication(event) {
  event.preventDefault();
  const formData = new FormData(event.currentTarget);
  const payload = Object.fromEntries(formData.entries());
  try {
    const data = await api("/api/applications", { method: "POST", body: JSON.stringify(payload) });
    showToast("Phase 1 workspace created locally.");
    await loadApplications();
    await loadDetail(data.application_id);
  } catch (error) { showToast(error.message, true); }
}

async function loadApplications() {
  try {
    const data = await api("/api/applications");
    state.applications = data.applications;
    renderList();
  } catch (error) { showToast(error.message, true); }
}

async function loadTemplates() {
  const templateData = await api("/api/templates");
  state.templates = templateData.templates || [];
  return state.templates;
}

async function loadDetail(applicationId) {
  try {
    const item = await api(`/api/applications/${encodeURIComponent(applicationId)}`);
    state.selected = applicationId;
    renderList();
    renderDetail(item);
  } catch (error) { showToast(error.message, true); }
}

function openDecision(action) {
  state.action = action;
  input.value = "";
  const title = document.querySelector("#dialog-title");
  const copy = document.querySelector("#dialog-copy");
  const label = document.querySelector("#decision-label");
  const submit = document.querySelector("#decision-submit");
  if (action === "approve") {
    title.textContent = "Approve exact documents";
    copy.textContent = "Type I_APPROVE_THE_DOCUMENTS. The approval is bound to the displayed SHA-256 hashes.";
    label.textContent = "Confirmation phrase";
    submit.textContent = "Approve documents";
    submit.className = "primary";
  } else if (action === "revision") {
    title.textContent = "Request a revision";
    copy.textContent = "Describe exactly what should change. Revised files must be rendered, staged, and approved again.";
    label.textContent = "Revision instructions";
    submit.textContent = "Send back for revision";
    submit.className = "secondary";
  } else {
    title.textContent = "Reject this package";
    copy.textContent = "This closes the package in Phase 2. No application will be submitted.";
    label.textContent = "Reason (optional)";
    submit.textContent = "Reject package";
    submit.className = "danger";
  }
  dialog.showModal();
  input.focus();
}

form.addEventListener("submit", async (event) => {
  if (event.submitter?.value === "cancel") return;
  event.preventDefault();
  const payload = { application_id: state.selected, action: state.action };
  if (state.action === "approve") payload.confirmation = input.value.trim();
  if (state.action === "revision") payload.instructions = input.value.trim();
  if (state.action === "reject") payload.reason = input.value.trim();
  try {
    await api("/api/action", { method: "POST", body: JSON.stringify(payload) });
    dialog.close();
    showToast("Decision recorded locally.");
    await loadApplications();
    await loadDetail(state.selected);
  } catch (error) { showToast(error.message, true); }
});

document.querySelector("#refresh").addEventListener("click", loadApplications);
document.querySelector("#new-application").addEventListener("click", renderWizard);

async function start() {
  try {
    const session = await api("/api/session");
    state.token = session.token;
    await loadTemplates();
    await loadApplications();
  } catch (error) { showToast(error.message, true); }
}

start();
