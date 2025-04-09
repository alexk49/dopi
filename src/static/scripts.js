function toggleDoiInputs() {
  const fileRadio = document.getElementById('file_radio');
  const textRadio = document.getElementById('text_radio');

  const doisUpload = document.getElementById('dois_upload');
  const doisText = document.getElementById('dois_text');
  const helperContainer = document.getElementById('doi_upload_helper_container');

  doisUpload.style.display = fileRadio.checked ? 'block' : 'none';
  doisText.style.display = textRadio.checked ? 'block' : 'none';
  helperContainer.style.display = fileRadio.checked ? 'block' : 'none';
}

document.addEventListener('DOMContentLoaded', () => {
  const fileRadio = document.getElementById('file_radio');
  const textRadio = document.getElementById('text_radio');

  fileRadio.addEventListener('click', toggleDoiInputs);
  textRadio.addEventListener('click', toggleDoiInputs);

});
