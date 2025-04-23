function toggleDoiInputs() {
  const fileRadio = document.getElementById('file_radio');
  const textRadio = document.getElementById('text_radio');

  const doisUpload = document.getElementById('dois_upload_wrapper');
  const doisText = document.getElementById('dois_text_wrapper');

  doisUpload.style.display = fileRadio.checked ? 'block' : 'none';
  doisText.style.display = textRadio.checked ? 'block' : 'none';
}


function countLines(event) {
  const counterEl = document.getElementById('dois_text_counter');

  const textarea = event.currentTarget;
  const lines = textarea.value.split("\n");
  const lineCount = lines.length;

  if (lineCount !== 1) {
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


async function handleFormSubmission(errorsDiv, messageDiv) {
    const form = this
    const formData = new FormData(form);

    errorsDiv.textContent = ''
    errorsDiv.innerHTML = ''

    result = await fetchFormResponse("/submit", formData)
    console.log(result)

    messageDiv.textContent = result.message;

    if (result.success) {
        messageDiv.style.color = 'green';
        form.reset();
        errorsDiv.innerHTML = ''
    } else {
        messageDiv.style.color = 'red';
        messageDiv.setAttribute('role', 'alert');
        messageDiv.setAttribute('aria-live', 'assertive');

        const errorList = Object.entries(result.errors).map(
          ([field, msg]) => `<li><strong>${field}</strong>: ${msg}</li>`
).join('');
        console.log("ERRORS: ")
        console.log(errorList)
        errorsDiv.innerHTML = `<ul>${errorList}</ul>`;
    }
}

document.addEventListener('DOMContentLoaded', () => {

  const doisText = document.getElementById('dois_text');
  doisText.addEventListener('input', countLines);

  const fileRadio = document.getElementById('file_radio');
  const textRadio = document.getElementById('text_radio');

  fileRadio.addEventListener('click', toggleDoiInputs);
  textRadio.addEventListener('click', toggleDoiInputs);

  const errorsDiv = document.getElementById('errors');
  const messageDiv = document.getElementById('message');

  document.getElementById('doi_submit_form').addEventListener('submit', async function(e) {
    e.preventDefault();
    handleFormSubmission(errorsDiv, messageDiv);
  });
});
