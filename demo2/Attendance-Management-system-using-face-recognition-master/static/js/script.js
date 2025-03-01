// Handle Add Face Form
document.getElementById('add-face-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData();
    formData.append('name', document.getElementById('name').value);
    formData.append('image', document.getElementById('image').files[0]);

    try {
        const response = await fetch('/add_face', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        alert(result.message);
    } catch (error) {
        alert('Error adding face: ' + error.message);
    }
});

// Handle Mark Attendance
// document.getElementById('mark-attendance').addEventListener('click', async () => {
//     try {
//         const response = await fetch('/mark_attendance', {
//             method: 'POST'
//         });
//         const result = await response.json();
//         alert(result.message);
//     } catch (error) {
//         alert('Error marking attendance: ' + error.message);
//     }
// });
    
document.getElementById('mark-attendance').addEventListener('click', async () => {
    try {
        const response = await fetch('/mark_attendance', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
        }

        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            const text = await response.text();
            throw new Error(`Invalid response format: ${text.substring(0, 100)}`);
        }

        const result = await response.json();
        if (result.status === 'success') {
            alert(result.message);
            document.getElementById('view-attendance').click();
        } else {
            alert(`Error: ${result.message}`);
        }
    } catch (error) {
        alert(`Attendance marking failed: ${error.message}`);
    }
});
// Handle View Attendance
document.getElementById('view-attendance').addEventListener('click', async () => {
    try {
        const response = await fetch('/view_attendance');
        const html = await response.text();
        document.getElementById('attendance-table').innerHTML = html;
    } catch (error) {
        alert('Error loading attendance: ' + error.message);
    }
});