const uploadBtn = document.getElementById('uploadBtn');
const fileInput = document.getElementById('fileInput');
const modal = document.getElementById('confirmationModal');
const modalTitle = document.getElementById('modalTitle');
const modalMessage = document.getElementById('modalMessage');
const confirmYes = document.getElementById('confirmYes');
const confirmNo = document.getElementById('confirmNo');
const clickCountDisplay = document.getElementById('clickCount');
const uploadCountDisplay = document.getElementById('uploadCount');
const frustrationDisplay = document.getElementById('frustration');
const logList = document.getElementById('logList');

let clickCount = 0;
let uploadCount = 0;
let confirmationLevel = 0;
let isMoving = false;

const buttonTexts = [
    'Click here',
    'No, here',
    'Actually, here...',
    'Try this one',
    'Nope, over here',
    'You\'ll never catch me!',
    'Keep trying...',
    'Getting closer...',
    'Almost...',
    'Just kidding, I\'m here!',
    'April fools!',
    'This is fun for me',
    'Seriously, come on',
    'Your persistence is admirable',
    'One more time...'
];

const confirmMessages = [
    {
        title: 'Are you SURE?',
        message: 'This action cannot be undone (jk it can)'
    },
    {
        title: 'Are you REALLY sure?',
        message: 'Like, super duper sure? No takebacks!'
    },
    {
        title: 'Are you REALLY REALLY sure?',
        message: 'Your file will be... *uploaded*. Think about it.'
    },
    {
        title: 'OK but like... are you sure?',
        message: 'Because I\'m uploading this bad boy now.'
    },
    {
        title: 'Fine. FINE. You win.',
        message: 'Your file is going to the cloud dimension.'
    }
];

const frustrationLevels = ['🙂', '😐', '😑', '😠', '🤬', '💥'];

// Move the button to a random position
function moveButton() {
    const uploadArea = document.querySelector('.upload-area');
    const rect = uploadArea.getBoundingClientRect();
    const containerRect = document.querySelector('.container').getBoundingClientRect();

    // Random position within bounds (leaving space for button size)
    const maxX = Math.max(rect.width - 150, 0);
    const maxY = Math.max(rect.height - 50, 0);

    const randomX = Math.random() * maxX;
    const randomY = Math.random() * maxY;

    uploadBtn.style.left = randomX + 'px';
    uploadBtn.style.top = randomY + 'px';
}

// Change button size randomly
function resizeButton() {
    const sizes = [0.8, 0.9, 1, 1.1, 1.2];
    const randomSize = sizes[Math.floor(Math.random() * sizes.length)];
    uploadBtn.style.transform = `scale(${randomSize})`;
}

// Change button text
function changeButtonText() {
    const randomText = buttonTexts[Math.floor(Math.random() * buttonTexts.length)];
    uploadBtn.textContent = randomText;
}

// Update frustration level
function updateFrustration() {
    const level = Math.min(clickCount, frustrationLevels.length - 1);
    frustrationDisplay.textContent = frustrationLevels[level];
}

// Make button move and change when user moves mouse over it
uploadBtn.addEventListener('mouseenter', () => {
    if (!isMoving) {
        moveButton();
        resizeButton();
        changeButtonText();
    }
});

// Click handler
uploadBtn.addEventListener('click', (e) => {
    e.preventDefault();
    clickCount++;
    clickCountDisplay.textContent = clickCount;
    updateFrustration();

    if (confirmationLevel < confirmMessages.length) {
        // Show confirmation modal
        const confirmation = confirmMessages[confirmationLevel];
        modalTitle.textContent = confirmation.title;
        modalMessage.textContent = confirmation.message;
        modal.classList.remove('hidden');
    }
});

// Confirmation Yes button
confirmYes.addEventListener('click', () => {
    confirmationLevel++;

    if (confirmationLevel >= confirmMessages.length) {
        // Actually upload
        modal.classList.add('hidden');
        fileInput.click();
    } else {
        // Ask again with more sarcasm
        const confirmation = confirmMessages[confirmationLevel];
        modalTitle.textContent = confirmation.title;
        modalMessage.textContent = confirmation.message;
    }
});

// Confirmation No button
confirmNo.addEventListener('click', () => {
    modal.classList.add('hidden');
    confirmationLevel = 0; // Reset to first confirmation
    addLogEntry('Upload cancelled by user (smart choice)', 'error');
});

// Handle actual file selection
fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        uploadFile(file);
    }
    confirmationLevel = 0; // Reset confirmation level
});

// Simulate file upload
function uploadFile(file) {
    uploadCount++;
    uploadCountDisplay.textContent = uploadCount;

    const fileName = file.name;
    const fileSize = (file.size / 1024).toFixed(2); // Convert to KB

    addLogEntry(`📁 ${fileName} (${fileSize} KB) - Uploading...`, 'default');

    // Simulate upload delay
    setTimeout(() => {
        addLogEntry(`✅ ${fileName} - Successfully tortured and stored!`, 'success');
    }, 1500 + Math.random() * 1000);
}

// Add entry to log
function addLogEntry(message, type = 'default') {
    // Remove empty message if it exists
    const emptyEntry = logList.querySelector('.log-entry.empty');
    if (emptyEntry) {
        emptyEntry.remove();
    }

    const li = document.createElement('li');
    li.className = `log-entry ${type}`;
    li.textContent = message;

    logList.insertBefore(li, logList.firstChild);

    // Keep only last 10 entries
    while (logList.children.length > 10) {
        logList.removeChild(logList.lastChild);
    }
}

// Start the troll behavior on page load
window.addEventListener('load', () => {
    moveButton();
    resizeButton();
    changeButtonText();

    // Every 2 seconds, move the button slightly
    setInterval(() => {
        if (!modal.classList.contains('hidden')) {
            // Don't move while modal is open
            return;
        }
        moveButton();
        resizeButton();
        changeButtonText();
    }, 2000);
});

// Close modal when clicking outside of it
modal.addEventListener('click', (e) => {
    if (e.target === modal) {
        modal.classList.add('hidden');
        confirmationLevel = 0;
    }
});
