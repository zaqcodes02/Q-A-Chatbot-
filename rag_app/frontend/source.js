// Function to send the query to the FastAPI backend
async function sendQuery(query) {
    const response = await fetch("http://localhost:8000/query", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: query }),
    });

    if (!response.ok) {
        throw new Error("Failed to fetch response from the server.");
    }

    return await response.json();
}

// Function to update the UI with the response
function updateUI(response) {
    const answerText = document.getElementById("answerText");
    const loadingSpinner = document.getElementById("loadingSpinner");

    // Hide the loading spinner
    loadingSpinner.style.display = "none";

    // Update the answer
    answerText.textContent = response.answer;
}

// Function to show the loading spinner and clear the previous answer
function showLoading() {
    const answerText = document.getElementById("answerText");
    const loadingSpinner = document.getElementById("loadingSpinner");

    // Clear the previous answer
    answerText.textContent = "";

    // Show the loading spinner
    loadingSpinner.style.display = "block";
}

// Event listener for the submit button
document.getElementById("submitButton").addEventListener("click", async () => {
    const queryInput = document.getElementById("queryInput");
    const query = queryInput.value.trim();

    if (query) {
        try {
            // Show loading spinner and clear previous answer
            showLoading();

            // Send the query to the backend
            const response = await sendQuery(query);

            // Update the UI with the response
            updateUI(response);
        } catch (error) {
            console.error("Error:", error);
            alert("An error occurred. Please try again.");
        }
    } else {
        alert("Please enter a question.");
    }
});