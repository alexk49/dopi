function countLines(event) {
  const counterEl = document.getElementById('dois_text_counter');

  const textarea = event.currentTarget;
  const lines = textarea.value.split("\n").filter(line => line.trim() !== "");
  const lineCount = lines.length;

  if (lineCount === 0) {
    counterEl.textContent = "";
  } else if (lineCount === 1) {
    counterEl.textContent = "1 Doi added";
  } else {
    counterEl.textContent = `${lineCount} Dois added`;
  }
}


async function fetchFormResponse(url, formData) {
    const response = await fetch(url, {
        method: 'POST',
        body: formData
    });
    return await response.json();
}


async function handleFormSubmission(form, errorsDiv, messageDiv) {
    const formData = new FormData(form);

    errorsDiv.textContent = ''
    errorsDiv.innerHTML = ''

    const result = await fetchFormResponse("/submit", formData)

    messageDiv.textContent = result.message;

    if (result.success) {
        messageDiv.style.color = 'green';
        form.reset();

        doisText.textContent = ''
        errorsDiv.innerHTML = ''
    } else {
        messageDiv.style.color = 'red';
        messageDiv.setAttribute('role', 'alert');
        messageDiv.setAttribute('aria-live', 'assertive');

        const errorList = Object.entries(result.errors).map(
          ([field, msg]) => `<li><strong>${field}</strong>: ${msg}</li>`
).join('');
        errorsDiv.innerHTML = `<ul>${errorList}</ul>`;
    }
}

document.addEventListener('DOMContentLoaded', () => {

  const doisText = document.getElementById('dois_text');
  doisText.addEventListener('input', countLines);

  const errorsDiv = document.getElementById('errors');
  const messageDiv = document.getElementById('message');
  const doiForm = document.getElementById('doi_submit_form');

  doiForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    messageDiv.textContent = ''

    handleFormSubmission(doiForm, errorsDiv, messageDiv, doisText);
  });
});
