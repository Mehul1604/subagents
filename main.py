from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from fastapi_mcp import FastApiMCP
from typing import List, Optional
from datetime import datetime
import uuid

app = FastAPI(title="Simple Form API", version="1.0.0")

mcp = FastApiMCP(app)

mcp.mount_http(app)

# In-memory storage for demo purposes
data_store: List[dict] = []


# Pydantic model for data validation
class DetailItem(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    message: str = Field(..., min_length=1, max_length=500)


class DetailResponse(BaseModel):
    id: str
    name: str
    email: str
    message: str
    created_at: str


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page with form and data display"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Simple Form API</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            h1 {
                color: white;
                text-align: center;
                margin-bottom: 30px;
                font-size: 2.5em;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            }
            .form-container, .data-container {
                background: white;
                border-radius: 10px;
                padding: 30px;
                margin-bottom: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            }
            h2 {
                color: #667eea;
                margin-bottom: 20px;
                border-bottom: 3px solid #667eea;
                padding-bottom: 10px;
            }
            .form-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 5px;
                color: #333;
                font-weight: 600;
            }
            input, textarea {
                width: 100%;
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 5px;
                font-size: 14px;
                transition: border-color 0.3s;
            }
            input:focus, textarea:focus {
                outline: none;
                border-color: #667eea;
            }
            textarea {
                resize: vertical;
                min-height: 100px;
            }
            button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                font-weight: 600;
                transition: transform 0.2s;
            }
            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }
            button:active {
                transform: translateY(0);
            }
            .data-item {
                background: #f8f9fa;
                border-left: 4px solid #667eea;
                padding: 15px;
                margin-bottom: 15px;
                border-radius: 5px;
            }
            .data-item strong {
                color: #667eea;
            }
            .data-item p {
                margin: 5px 0;
            }
            .message {
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 20px;
                display: none;
            }
            .message.success {
                background: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
            .message.error {
                background: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }
            .no-data {
                text-align: center;
                color: #999;
                padding: 30px;
                font-style: italic;
            }
            .refresh-btn {
                background: #28a745;
                margin-bottom: 20px;
            }
            .clear-btn {
                background: #dc3545;
                margin-left: 10px;
            }
            .edit-btn {
                background: #007bff;
                padding: 8px 16px;
                font-size: 14px;
                margin-top: 10px;
            }
            .delete-btn {
                background: #dc3545;
                padding: 8px 16px;
                font-size: 14px;
                margin-top: 10px;
                margin-left: 10px;
            }
            .modal {
                display: none;
                position: fixed;
                z-index: 1000;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0,0,0,0.5);
            }
            .modal-content {
                background-color: white;
                margin: 5% auto;
                padding: 30px;
                border-radius: 10px;
                width: 90%;
                max-width: 600px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            }
            .modal-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
            }
            .close-btn {
                background: #6c757d;
                padding: 8px 16px;
                font-size: 14px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Simple Form API</h1>

            <div class="form-container">
                <h2>Submit Details</h2>
                <div id="statusMessage" class="message"></div>
                <form id="detailsForm">
                    <div class="form-group">
                        <label for="name">Name:</label>
                        <input type="text" id="name" name="name" required>
                    </div>
                    <div class="form-group">
                        <label for="email">Email:</label>
                        <input type="email" id="email" name="email" required>
                    </div>
                    <div class="form-group">
                        <label for="message">Message:</label>
                        <textarea id="message" name="message" required></textarea>
                    </div>
                    <button type="submit">Submit</button>
                </form>
            </div>

            <div class="data-container">
                <h2>Submitted Details</h2>
                <button class="refresh-btn" onclick="loadData()">Refresh Data</button>
                <button class="clear-btn" onclick="clearAllData()">Clear All</button>
                <div id="dataDisplay"></div>
            </div>
        </div>

        <!-- Edit Modal -->
        <div id="editModal" class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Edit Detail</h2>
                    <button class="close-btn" onclick="closeEditModal()">Close</button>
                </div>
                <div id="editStatusMessage" class="message"></div>
                <form id="editForm">
                    <input type="hidden" id="editId">
                    <div class="form-group">
                        <label for="editName">Name:</label>
                        <input type="text" id="editName" name="name" required>
                    </div>
                    <div class="form-group">
                        <label for="editEmail">Email:</label>
                        <input type="email" id="editEmail" name="email" required>
                    </div>
                    <div class="form-group">
                        <label for="editMessage">Message:</label>
                        <textarea id="editMessage" name="message" required></textarea>
                    </div>
                    <button type="submit">Update</button>
                    <button type="button" class="close-btn" onclick="closeEditModal()">Cancel</button>
                </form>
            </div>
        </div>

        <script>
            // Load data on page load
            document.addEventListener('DOMContentLoaded', loadData);

            // Handle form submission
            document.getElementById('detailsForm').addEventListener('submit', async (e) => {
                e.preventDefault();

                const formData = {
                    name: document.getElementById('name').value,
                    email: document.getElementById('email').value,
                    message: document.getElementById('message').value
                };

                try {
                    const response = await fetch('/postDetails', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(formData)
                    });

                    if (response.ok) {
                        const result = await response.json();
                        showMessage('Data submitted successfully!', 'success');
                        document.getElementById('detailsForm').reset();
                        loadData();
                    } else {
                        const error = await response.json();
                        showMessage('Error: ' + (error.detail || 'Submission failed'), 'error');
                    }
                } catch (error) {
                    showMessage('Error: ' + error.message, 'error');
                }
            });

            // Load and display data
            async function loadData() {
                try {
                    const response = await fetch('/getDetails');
                    const data = await response.json();

                    const displayDiv = document.getElementById('dataDisplay');

                    if (data.length === 0) {
                        displayDiv.innerHTML = '<div class="no-data">No data submitted yet. Fill out the form above to get started!</div>';
                        return;
                    }

                    displayDiv.innerHTML = data.map(item => `
                        <div class="data-item">
                            <p><strong>Name:</strong> ${escapeHtml(item.name)}</p>
                            <p><strong>Email:</strong> ${escapeHtml(item.email)}</p>
                            <p><strong>Message:</strong> ${escapeHtml(item.message)}</p>
                            <p><strong>Submitted:</strong> ${item.created_at}</p>
                            <p style="color: #999; font-size: 0.9em;"><strong>ID:</strong> ${item.id}</p>
                            <button class="edit-btn" onclick='openEditModal(${JSON.stringify(item)})'>Edit</button>
                            <button class="delete-btn" onclick='deleteDetail("${item.id}")'>Delete</button>
                        </div>
                    `).join('');
                } catch (error) {
                    document.getElementById('dataDisplay').innerHTML =
                        '<div class="message error">Error loading data: ' + error.message + '</div>';
                }
            }

            // Clear all data
            async function clearAllData() {
                if (!confirm('Are you sure you want to clear all data?')) {
                    return;
                }

                try {
                    const response = await fetch('/clearDetails', {
                        method: 'DELETE'
                    });

                    if (response.ok) {
                        showMessage('All data cleared successfully!', 'success');
                        loadData();
                    } else {
                        showMessage('Error clearing data', 'error');
                    }
                } catch (error) {
                    showMessage('Error: ' + error.message, 'error');
                }
            }

            // Delete individual detail
            async function deleteDetail(detailId) {
                if (!confirm('Are you sure you want to delete this detail?')) {
                    return;
                }

                try {
                    const response = await fetch(`/deleteDetails/${detailId}`, {
                        method: 'DELETE'
                    });

                    if (response.ok) {
                        const result = await response.json();
                        showMessage('Detail deleted successfully!', 'success');
                        loadData();
                    } else {
                        const error = await response.json();
                        showMessage('Error: ' + (error.detail || 'Delete failed'), 'error');
                    }
                } catch (error) {
                    showMessage('Error: ' + error.message, 'error');
                }
            }

            // Show message
            function showMessage(text, type) {
                const messageDiv = document.getElementById('statusMessage');
                messageDiv.textContent = text;
                messageDiv.className = 'message ' + type;
                messageDiv.style.display = 'block';

                setTimeout(() => {
                    messageDiv.style.display = 'none';
                }, 5000);
            }

            // Escape HTML to prevent XSS
            function escapeHtml(text) {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }

            // Open edit modal
            function openEditModal(item) {
                document.getElementById('editId').value = item.id;
                document.getElementById('editName').value = item.name;
                document.getElementById('editEmail').value = item.email;
                document.getElementById('editMessage').value = item.message;
                document.getElementById('editModal').style.display = 'block';
            }

            // Close edit modal
            function closeEditModal() {
                document.getElementById('editModal').style.display = 'none';
                document.getElementById('editForm').reset();
                const editMessageDiv = document.getElementById('editStatusMessage');
                editMessageDiv.style.display = 'none';
            }

            // Handle edit form submission
            document.getElementById('editForm').addEventListener('submit', async (e) => {
                e.preventDefault();

                const detailId = document.getElementById('editId').value;
                const formData = {
                    name: document.getElementById('editName').value,
                    email: document.getElementById('editEmail').value,
                    message: document.getElementById('editMessage').value
                };

                try {
                    const response = await fetch(`/updateDetails/${detailId}`, {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(formData)
                    });

                    if (response.ok) {
                        const result = await response.json();
                        showMessage('Detail updated successfully!', 'success');
                        closeEditModal();
                        loadData();
                    } else {
                        const error = await response.json();
                        showEditMessage('Error: ' + (error.detail || 'Update failed'), 'error');
                    }
                } catch (error) {
                    showEditMessage('Error: ' + error.message, 'error');
                }
            });

            // Show message in edit modal
            function showEditMessage(text, type) {
                const messageDiv = document.getElementById('editStatusMessage');
                messageDiv.textContent = text;
                messageDiv.className = 'message ' + type;
                messageDiv.style.display = 'block';

                setTimeout(() => {
                    messageDiv.style.display = 'none';
                }, 5000);
            }

            // Close modal when clicking outside
            window.onclick = function(event) {
                const modal = document.getElementById('editModal');
                if (event.target === modal) {
                    closeEditModal();
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.post("/postDetails", response_model=DetailResponse)
async def post_details(detail: DetailItem):
    print("Received detail submission:", detail)
    """
    POST endpoint to submit new details
    """
    # Create a new detail entry
    new_detail = {
        "id": str(uuid.uuid4()),
        "name": detail.name,
        "email": detail.email,
        "message": detail.message,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    data_store.append(new_detail)

    return DetailResponse(**new_detail)


@app.get("/getDetails", response_model=List[DetailResponse])
async def get_details():
    """
    GET endpoint to retrieve all submitted details
    """
    return [DetailResponse(**item) for item in data_store]


@app.get("/getDetails/{detail_id}", response_model=DetailResponse)
async def get_detail_by_id(detail_id: str):
    """
    GET endpoint to retrieve a specific detail by ID
    """
    for item in data_store:
        if item["id"] == detail_id:
            return DetailResponse(**item)

    raise HTTPException(status_code=404, detail="Detail not found")


@app.put("/updateDetails/{detail_id}", response_model=DetailResponse)
async def update_detail(detail_id: str, detail: DetailItem):
    """
    PUT endpoint to update an existing detail by ID
    """
    for item in data_store:
        if item["id"] == detail_id:
            # Update the fields while preserving id and created_at
            item["name"] = detail.name
            item["email"] = detail.email
            item["message"] = detail.message
            return DetailResponse(**item)

    raise HTTPException(status_code=404, detail="Detail not found")


@app.delete("/deleteDetails/{detail_id}")
async def delete_detail(detail_id: str):
    """
    DELETE endpoint to delete a specific detail by ID
    """
    for i, item in enumerate(data_store):
        if item["id"] == detail_id:
            data_store.pop(i)
            return {
                "message": "Detail deleted successfully",
                "deleted_id": detail_id,
                "remaining_count": len(data_store)
            }

    raise HTTPException(status_code=404, detail="Detail not found")


@app.delete("/clearDetails")
async def clear_details():
    """
    DELETE endpoint to clear all stored details
    """
    data_store.clear()
    return {"message": "All details cleared successfully", "count": 0}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "total_records": len(data_store)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
