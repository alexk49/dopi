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

async function fetchServerData(url) {
    const response = await fetch(url, {
        method: 'GET'
    });
    return await response.json()
}

async function fetchFormResponse(url, formData) {
    const response = await fetch(url, {
        method: 'POST',
        body: formData
    });
    return await response.json();
}

async function updateQueueCounter(queueCounterEl) {
    const result = await fetchServerData("/queue")
    const queue_count = result.queue_count
    
    if (queue_count === '1') {
      queueCounterEl.innerHTML = `There is ${queue_count} file in the queue to be processed.`
    } else {
      queueCounterEl.innerHTML = `There are ${queue_count} files in the queue to be processed.`
    }
}

async function updateCompletedFiles(completedFilesEl) {
    const result = await fetchServerData("/completed")
    const completed = result.completed
    
    if (completed && Array.isArray(completed)) {
          completedFilesEl.innerHTML = `
        <ul id="completed-files-list">
        </ul>`;

          const ulElement = document.getElementById("completed-files-list");
          
          completed.forEach(filename => {
            const li = document.createElement("li");
            li.innerHTML = `<a href="/complete/${filename}">${filename}</a>`;
            ulElement.appendChild(li);
          });
    }
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

  /* set up queue toggle */
  const showQueueButton = document.getElementById('show_queue_counter');
  const queueCounter = document.getElementById('queue_counter');

  if (showQueueButton !== null && queueCounter !== null) {
    showQueueButton.addEventListener('click', async () => {

      if (queueCounter.hidden) {
        await updateQueueCounter(queueCounter);
        queueCounter.hidden = false;
      }
      else {
        queueCounter.hidden = true;
      }
    });
  }
  
  /* set up complete files toggle */
  const showCompletedButton = document.getElementById('show_completed_files');
  const completedFilesEl = document.getElementById('completed_files');
  if (showCompletedButton !== null && completedFilesEl !== null) {
    showCompletedButton.addEventListener('click', async () => {

      if (completedFilesEl.hidden) {
        await updateCompletedFiles(completedFilesEl);
        completedFilesEl.hidden = false;
      }
      else {
        completedFilesEl.hidden = true;
      }
    });
  }

  /* set up doi counter */
  const doisText = document.getElementById('dois_text');

  if (doisText !== null) {
    doisText.addEventListener('input', countLines);
  }

  /* set up form handler / submission */
  const errorsDiv = document.getElementById('errors');
  const messageDiv = document.getElementById('message');
  const doiForm = document.getElementById('doi_submit_form');

  if (doiForm !== null) {
    doiForm.addEventListener('submit', async function(e) {
      e.preventDefault();
      messageDiv.textContent = ''

      handleFormSubmission(doiForm, errorsDiv, messageDiv, doisText);
    });
  }
});
