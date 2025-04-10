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

document.addEventListener('DOMContentLoaded', () => {

  const doisText = document.getElementById('dois_text');
  doisText.addEventListener('input', countLines);

  const fileRadio = document.getElementById('file_radio');
  const textRadio = document.getElementById('text_radio');

  fileRadio.addEventListener('click', toggleDoiInputs);
  textRadio.addEventListener('click', toggleDoiInputs);

});
