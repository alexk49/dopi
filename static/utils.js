export function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
  return null;
}

export async function toggleElVisibility(el, onShowCallback) {
  if (el.hidden) {
    el.hidden = false;
    if (onShowCallback) await onShowCallback();
  } else {
    el.hidden = true;
  }
  return !el.hidden;
}

export function countLines(counterEl, textAreaEl) {
  const lines = textAreaEl.value
    .split("\n")
    .filter((line) => line.trim() !== "");
  const lineCount = lines.length;

  if (lineCount === 0) {
    counterEl.textContent = "";
  } else if (lineCount === 1) {
    counterEl.textContent = "1 Doi added";
  } else {
    counterEl.textContent = `${lineCount} Dois added`;
  }
}

export async function fetchServerData(url) {
  try {
    const response = await fetch(url);
    if (!response.ok)
      throw new Error(`HTTP error: ${response.status}`);
    return await response.json();
  } catch (error) {
    let err_msg = `Error fetching data from: ${url}, ${error}`
    console.error(err_msg);
    return { 'success': 'false', 'message': err_msg }
  }
}

export async function fetchQueueCount() {
  const result = await fetchServerData("/queue");
  return result.queue_count;
}

export async function fetchFormResponse(url, formData) {
  try {
    const response = await fetch(url, {
      method: "POST",
      body: formData,
    });
    if (!response.ok) throw new Error(`HTTP error: ${response.status}`);
    return await response.json();
  } catch (error) {
    let err_msg = `Error posting form data to: ${url} - ${error}`
    console.error(err_msg);
    return { 'success': 'false', 'message': err_msg }
  }
}

export function updateQueueCounter(queueCounterEl, queueCount) {
  if (queueCount === "1") {
    queueCounterEl.textContent = `There is ${queueCount} file in the queue to be processed.`;
  } else {
    queueCounterEl.textContent = `There are ${queueCount} files in the queue to be processed.`;
  }
}

export function buildCompletedFilesList(filenames) {
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

export function clearErrors(errorsDiv) {
  errorsDiv.textContent = "";
  errorsDiv.innerHTML = "";
}

export async function fetchCompleteFiles() {
  const result = await fetchServerData("/completed");
  return result.completed;
}

export async function updateCompletedFiles(completedFilesEl, completedFiles) {
  if (completedFiles && Array.isArray(completedFiles)) {
    completedFilesEl.innerHTML = "";

    const ulElement = buildCompletedFilesList(completedFiles);
    completedFilesEl.appendChild(ulElement);
  }
}

export function showMessage(messageDiv, message, isSuccess) {
  messageDiv.textContent = message;
  messageDiv.style.color = isSuccess ? "green" : "red";

  if (!isSuccess) {
    messageDiv.setAttribute("role", "alert");
    messageDiv.setAttribute("aria-live", "assertive");
  } else {
    messageDiv.removeAttribute("role");
    messageDiv.removeAttribute("aria-live");
  }
}

export function handleFormSuccess(form, doisText, errorsDiv) {
  form.reset();
  doisText.textContent = "";
  clearErrors(errorsDiv);
}

export function handleFormErrors(errorsDiv, errors) {
  const errorList = Object.entries(errors)
    .map(([field, msg]) => `<li><strong>${field}</strong>: ${msg}</li>`)
    .join("");

  errorsDiv.innerHTML = `<ul>${errorList}</ul>`;
}

export async function fetchAndUpdateQueueCounter(queueCounterEl) {
  const queueCount = await fetchQueueCount();
  updateQueueCounter(queueCounterEl, queueCount);
}

export async function fetchAndUpdateCompletedFiles(completedFilesEl) {
  const completedFiles = await fetchCompleteFiles();
  updateCompletedFiles(completedFilesEl, completedFiles);
}

export async function handleFormSubmission(
  form,
  errorsDiv,
  messageDiv,
  doisText,
) {
  const formData = new FormData(form);
  clearErrors(errorsDiv);

  const result = await fetchFormResponse("/submit", formData);

  console.log(result)

  showMessage(messageDiv, result.message, result.success);

  if (result.success) {
    handleFormSuccess(form, doisText, errorsDiv);
  } else {
    handleFormErrors(messageDiv, errorsDiv, result.errors);
  }
}
