function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
  return null;
}

function toggleElVisibility(el, onShowCallback) {
  if (el.hidden) {
    if (onShowCallback) onShowCallback();
    el.hidden = false;
  } else {
    el.hidden = true;
  }
}

function countLines(event) {
  const counterEl = document.getElementById("dois_text_counter");

  const textarea = event.currentTarget;
  const lines = textarea.value.split("\n").filter((line) => line.trim() !== "");
  const lineCount = lines.length;

  if (lineCount === 0) {
    counterEl.textContent = "";
  } else if (lineCount === 1) {
    counterEl.textContent = "1 Doi added";
  } else {
    counterEl.textContent = `${lineCount} Dois added`;
  }
}

async function fetchServerData(url) {
  try {
    const response = await fetch(url);
    if (!response.ok)
      throw new Error(`HTTP error: ${response.status} - ${response}`);
    return await response.json();
  } catch (error) {
    console.error(`Error fetching data from: ${url}, error: ${error}`);
    return {};
  }
}

async function fetchFormResponse(url, formData) {
  try {
    const response = await fetch(url, {
      method: "POST",
      body: formData,
    });
    if (!response.ok) throw new Error(`HTTP error: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error(
      `Error posting form data to: ${url} - error: ${error}, form-data: ${formData}`,
    );
    return {};
  }
}

async function updateQueueCounter(queueCounterEl) {
  const result = await fetchServerData("/queue");
  const queueCount = result.queue_count;

  if (queueCount === "1") {
    queueCounterEl.textContent = `There is ${queueCount} file in the queue to be processed.`;
  } else {
    queueCounterEl.textContent = `There are ${queueCount} files in the queue to be processed.`;
  }
}

function buildCompletedFilesList(filenames) {
  const ul = document.createElement("ul");
  ul.id = "completed-files-list";

  filenames.forEach((filename) => {
    const li = document.createElement("li");
    const a = document.createElement("a");
    a.href = `/complete/${filename}`;
    a.textContent = filename;
    li.appendChild(a);
    ul.appendChild(li);
  });

  return ul;
}

async function updateCompletedFiles(completedFilesEl) {
  const result = await fetchServerData("/completed");
  const completed = result.completed;

  if (completed && Array.isArray(completed)) {
    completedFilesEl.innerHTML = "";

    const ulElement = buildCompletedFilesList(completed);
    completedFilesEl.appendChild(ulElement);
  }
}

async function handleFormSubmission(form, errorsDiv, messageDiv, doisText) {
  const formData = new FormData(form);

  errorsDiv.textContent = "";
  errorsDiv.innerHTML = "";

  const result = await fetchFormResponse("/submit", formData);

  messageDiv.textContent = result.message;

  if (result.success) {
    messageDiv.style.color = "green";
    form.reset();
    doisText.textContent = "";
    errorsDiv.innerHTML = "";
  } else {
    messageDiv.style.color = "red";
    messageDiv.setAttribute("role", "alert");
    messageDiv.setAttribute("aria-live", "assertive");

    const errorList = Object.entries(result.errors)
      .map(([field, msg]) => `<li><strong>${field}</strong>: ${msg}</li>`)
      .join("");
    errorsDiv.innerHTML = `<ul>${errorList}</ul>`;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  /* populate csrf token in submit form */
  document.getElementById("csrf_token").value = getCookie("csrf_token");

  /* set up queue toggle */
  const showQueueButton = document.getElementById("show_queue_counter");
  const queueCounter = document.getElementById("queue_counter");

  if (showQueueButton !== null && queueCounter !== null) {
    showQueueButton.addEventListener("click", async () => {
      toggleElVisibility(queueCounter, () => updateQueueCounter(queueCounter));
    });
  }

  /* set up complete files toggle */
  const showCompletedButton = document.getElementById("show_completed_files");
  const completedFilesEl = document.getElementById("completed_files");

  if (showCompletedButton !== null && completedFilesEl !== null) {
    showCompletedButton.addEventListener("click", async () => {
      toggleElVisibility(completedFilesEl, () =>
        updateCompletedFiles(completedFilesEl),
      );
    });
  }

  /* set up doi counter */
  const doisText = document.getElementById("dois_text");

  if (doisText !== null) {
    doisText.addEventListener("input", countLines);
  }

  /* set up form handler / submission */
  const errorsDiv = document.getElementById("errors");
  const messageDiv = document.getElementById("message");
  const doiForm = document.getElementById("doi_submit_form");

  if (doiForm !== null) {
    doiForm.addEventListener("submit", async function (e) {
      e.preventDefault();
      messageDiv.textContent = "";

      handleFormSubmission(doiForm, errorsDiv, messageDiv, doisText);
    });
  }
});
