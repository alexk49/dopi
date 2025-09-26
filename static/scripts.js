import {
  getCookie,
  fetchAndUpdateQueueCounter,
  fetchAndUpdateCompletedFiles,
  handleFormSubmission,
  toggleElVisibility,
  countLines,
} from "./utils.js";

function addEmail() {
  const link = document.createElement("a");
  const email = "hello@booksanon.com";
  link.href = `mailto:${email}`;
  link.textContent = email;
  document.getElementById("email-link").appendChild(link);
}

function setupCSRFToken() {
  const csrfTokenField = document.getElementById("csrf_token");
  if (csrfTokenField) {
    csrfTokenField.value = getCookie("csrf_token");
  }
}

function setupQueueCounter() {
  const showQueueButton = document.getElementById("show_queue_counter");
  const queueCounter = document.getElementById("queue_counter");

  if (!showQueueButton || !queueCounter) return;

  showQueueButton.addEventListener("click", async () => {
    await toggleElVisibility(queueCounter, async () => {
      await fetchAndUpdateQueueCounter(queueCounter);
    });
  });
}

function setupCompletedFilesToggle() {
  const showCompletedButton = document.getElementById("show_completed_files");
  const completedFilesEl = document.getElementById("completed_files");

  if (!showCompletedButton || !completedFilesEl) return;

  showCompletedButton.addEventListener("click", async () => {
    await toggleElVisibility(completedFilesEl, async () => {
      await fetchAndUpdateCompletedFiles(completedFilesEl);
    });
  });
}

function setupDOICounter() {
  const doisTextEl = document.getElementById("dois_text");
  const counterEl = document.getElementById("dois_text_counter");

  if (!doisTextEl || !counterEl) return;

  doisTextEl.addEventListener("input", () => countLines(counterEl, doisTextEl));
}

function setupFormSubmission() {
  const doiForm = document.getElementById("doi_submit_form");
  const errorsDiv = document.getElementById("errors");
  const messageDiv = document.getElementById("message");
  const doisTextEl = document.getElementById("dois_text");
  const doisTextCounterEl = document.getElementById("dois_text_counter");

  if (!doiForm || !errorsDiv || !messageDiv) return;

  doiForm.addEventListener("submit", async function (e) {
    e.preventDefault();
    messageDiv.textContent = "";
    await handleFormSubmission(
      doiForm,
      errorsDiv,
      messageDiv,
      doisTextEl,
      doisTextCounterEl,
    );
  });
}

document.addEventListener("DOMContentLoaded", () => {
  addEmail();
  setupCSRFToken();
  setupQueueCounter();
  setupCompletedFilesToggle();
  setupDOICounter();
  setupFormSubmission();
});
