// static/js/detectcrime.js

// Function to handle training model logic
function sendTrainModelRequest() {
    const statusCard = document.getElementById('statusCard');
    const loadingMessage = document.getElementById('loadingMessage');
    const responseMessage = document.getElementById('responseMessage');

    statusCard.style.display = 'block';
    loadingMessage.style.display = 'block';
    loadingMessage.textContent = "Training model... Please wait.";
    responseMessage.style.display = 'none';

    const formData = new FormData();
    formData.append('action', 'train'); // Specify the action for training the model

    // Send the AJAX request
    fetch(trainModelUrl, {
        method: "POST",
        body: formData,
        headers: {
            "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
        }
    })
    .then(response => response.json())
    .then(data => {
        // Hide "Training model... Please wait." message
        loadingMessage.style.display = "none";

        // Display the result message
        responseMessage.textContent = data.message;
        if (data.message.includes("successfully")) {
            responseMessage.className = "status-success"; // Success message
        } else {
            responseMessage.className = "status-error"; // Failure message
        }

        responseMessage.style.display = 'block';

        // Fade out the status card after 3 seconds
        setTimeout(() => {
            statusCard.classList.add('fade-out');
            setTimeout(() => {
                statusCard.style.display = 'none';
                statusCard.classList.remove('fade-out');
            }, 1000); // Match the transition duration
        }, 3000);
    })
    .catch(error => {
        // Hide "Training model... Please wait." message
        loadingMessage.style.display = "none";

        // Display error message
        responseMessage.textContent = `Error: ${error}`;
        responseMessage.className = "status-error";
        responseMessage.style.display = 'block';
    });
}

// Function to handle loading model logic
function sendLoadModelRequest() {
    const statusCard = document.getElementById('statusCard');
    const loadingMessage = document.getElementById('loadingMessage');
    const responseMessage = document.getElementById('responseMessage');

    // Show "Loading model... Please wait." message
    statusCard.style.display = 'block';
    loadingMessage.style.display = "block";
    loadingMessage.textContent = "Loading model... Please wait.";
    responseMessage.textContent = ""; // Clear any previous message

    const formData = new FormData();
    formData.append('action', 'load_model'); // Specify the action for loading the model

    // Send the AJAX request
    fetch(loadModelUrl, {
        method: "POST",
        body: formData,
        headers: {
            "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
        }
    })
    .then(response => response.json())
    .then(data => {
        // Hide "Loading model... Please wait." message
        loadingMessage.style.display = "none";

        // Display the result message
        responseMessage.textContent = data.message;
        if (data.message.includes("successfully")) {
            responseMessage.className = "status-success"; // Success message
        } else {
            responseMessage.className = "status-error"; // Failure message
        }

        responseMessage.style.display = 'block';

        // Fade out the status card after 3 seconds
        setTimeout(() => {
            statusCard.classList.add('fade-out');
            setTimeout(() => {
                statusCard.style.display = 'none';
                statusCard.classList.remove('fade-out');
            }, 1000); // Match the transition duration
        }, 3000);
    })
    .catch(error => {
        // Hide "Loading model... Please wait." message
        loadingMessage.style.display = "none";

        // Display error message
        responseMessage.textContent = `Error: ${error}`;
        responseMessage.className = "status-error";
        responseMessage.style.display = 'block';
    });
}

// Function to handle showing graph logic
function sendShowGraphRequest(graphType) {
    const graphCard = document.getElementById('graphCard');
    const graphImage = document.getElementById('graphImage');

    graphCard.style.display = 'block';
    graphImage.src = ""; // Clear any previous image

    const formData = new FormData();
    formData.append('action', 'show_graph'); // Specify the action for showing the graph
    formData.append('graph_type', graphType); // Specify the graph type

    // Send the AJAX request
    fetch(showGraphUrl, {
        method: "POST",
        body: formData,
        headers: {
            "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.graph_url) {
            graphImage.src = data.graph_url;
        } else {
            graphImage.alt = "Error loading graph";
        }
    })
    .catch(error => {
        graphImage.alt = `Error: ${error}`;
    });
}

// Attach event listeners to the buttons
document.addEventListener('DOMContentLoaded', (event) => {
    document.getElementById('trainButton').addEventListener('click', sendTrainModelRequest);
    document.getElementById('loadModelButtonDC').addEventListener('click', sendLoadModelRequest);

    // Attach event listeners for different graph types
    document.getElementById('showCrimeTypesGraphButton').addEventListener('click', () => sendShowGraphRequest('crime_types'));
    document.getElementById('showVictimAgeGraphButton').addEventListener('click', () => sendShowGraphRequest('victim_age'));
    document.getElementById('showCrimeAreasGraphButton').addEventListener('click', () => sendShowGraphRequest('crime_areas'));
});