tinymce.init({
    selector: '#description',
    menubar: false,
    plugins: 'link image code',
    toolbar: 'undo redo | bold italic | alignleft aligncenter alignright | code'
});

const uploadBox = document.getElementById('uploadBox');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const fileError = document.getElementById('fileError');
const reuploadBtn = document.getElementById('reuploadBtn');
const fileTypeSelect = document.getElementById('fileType');

function getFileExtensions() {
    const selectedOption = fileTypeSelect.options[fileTypeSelect.selectedIndex];
    return selectedOption.getAttribute('data-extensions').split(',');
}

function handleFileUpload(file) {
    if (!file) return;

    const fileName = file.name;
    const fileExtension = fileName.split('.').pop().toLowerCase();
    const allowedExtensions = getFileExtensions();

    if (allowedExtensions.includes(fileExtension)) {
        fileError.textContent = '';
        fileInfo.innerHTML = `<i class="bi bi-file-earmark"></i> Selected file (${fileExtension}): ${fileName}`;
        reuploadBtn.style.display = 'block';
    } else {
        fileInfo.textContent = '';
        fileError.textContent = 'Invalid file type. Please upload a valid file.';
        fileInput.value = '';
        reuploadBtn.style.display = 'none';
    }
}

function resetFileInput() {
    fileInput.value = '';
    fileInfo.textContent = '';
    fileError.textContent = '';
    reuploadBtn.style.display = 'none';
}

uploadBox.addEventListener('click', () => fileInput.click());
uploadBox.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadBox.style.borderColor = '#3b82f6';
});
uploadBox.addEventListener('dragleave', () => {
    uploadBox.style.borderColor = '#ccc';
});
uploadBox.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadBox.style.borderColor = '#ccc';
    handleFileUpload(e.dataTransfer.files[0]);
});

fileInput.addEventListener('change', (e) => {
    handleFileUpload(e.target.files[0]);
});

reuploadBtn.addEventListener('click', () => {
    fileInput.click();
});

fileTypeSelect.addEventListener('change', () => {
    resetFileInput();
});

document.getElementById('uploadForm').addEventListener('submit', (e) => {
    const fileExtension = (fileInput.files[0] ? fileInput.files[0].name.split('.').pop().toLowerCase() : '');
    const allowedExtensions = getFileExtensions();

    if (!fileInput.files[0] || !allowedExtensions.includes(fileExtension)) {
        e.preventDefault();
        fileError.textContent = 'Please upload a valid file before submitting.';
    }
});