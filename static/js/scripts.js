let selectedFolder = null; // Track the selected folder

document.getElementById("fileInput").addEventListener("change", function(event) {
    const file = event.target.files[0];
    if (file) {
        // Upload the file to the server
        uploadImage(file);

        // Display the image locally
        const imageUrl = URL.createObjectURL(file);
        document.getElementById("image").src = imageUrl;
    }
});

function uploadImage(file) {
    const formData = new FormData();
    formData.append('file', file);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Image uploaded successfully');
            refreshFolderList(data.folders); // Update the folder list with the response folders
        } else {
            alert('Error uploading image');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function addFolder() {
    const folderName = prompt("Enter folder name:");
    if (folderName) {
        fetch('/create_folder', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ folder_name: folderName }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Folder created successfully');
                refreshFolderList();
            } else {
                alert('Error creating folder');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
}

function deleteFolder(folderName) {
    fetch('/delete_folder', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ folder_name: folderName }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Folder deleted successfully');
            refreshFolderList();
        } else {
            alert('Error deleting folder');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function refreshFolderList() {
    fetch('/get_folders')
    .then(response => response.json())
    .then(data => {
        const foldersContainer = document.querySelector('.folders');
        foldersContainer.innerHTML = '';
        data.folders.forEach(folder => {
            const folderElement = document.createElement('div');
            folderElement.textContent = folder;
            
            const deleteButton = document.createElement('button');
            deleteButton.textContent = 'X';
            deleteButton.addEventListener('click', (event) => {
                event.stopPropagation();
                deleteFolder(folder);
            });

            folderElement.appendChild(deleteButton);

            folderElement.addEventListener('click', () => {
                selectedFolder = folder; // Set the selected folder
                getFolderContents(folder);
            });

            foldersContainer.appendChild(folderElement);
        });
    });
}

function getFolderContents(folderPath) {
    fetch(`/get_folder_contents/${encodeURIComponent(folderPath)}`)
    .then(response => response.json())
    .then(data => {
        const contentsContainer = document.querySelector('.folder-contents');
        contentsContainer.innerHTML = '';
        data.contents.forEach(content => {
            const contentElement = document.createElement('div');
            contentElement.textContent = content.name;
            if (content.type === 'folder') {
                contentElement.addEventListener('click', () => {
                    selected
