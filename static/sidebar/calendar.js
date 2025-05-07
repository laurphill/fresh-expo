const monthYearElement = document.getElementById('monthYear');
const datesElement = document.getElementById('dates');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
 
document.addEventListener('DOMContentLoaded', function() {
  var calendarEl = document.getElementById('calendar');
  var containerEl = document.getElementById('myUL');

  // Make to-do list items draggable
  new FullCalendar.Draggable(containerEl, {
    itemSelector: 'li', // Select draggable items
    eventData: function(eventEl) {
      return {
        title: eventEl.getAttribute('data-title'), // Use the data-title attribute for the event title
      };
    }
  });
  var calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: 'dayGridMonth',
    headerToolbar: {
      left: 'prev,next today',
      center: 'title',
      right: 'addEventButton,dayGridMonth,timeGridWeek,timeGridDay'
    },
    editable: true,
    droppable: true, // this allows things to be dropped onto the calendar
    events: eventsData, // Pass events from Flask to FullCalendar
    
    

    // Handle event drag and drop
    eventDrop: function(info) {
    // Log the updated event details for debugging
      console.log('Event dropped:', info.event);

      // Send an UPDATE request to the backend
      fetch(`/api/events/${info.event.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          id: info.event.id, // Use the actual event ID
          title: info.event.title,
          start: info.event.start.toISOString(), // Convert to ISO string
        }),
      })
      .then(response => response.json())
      
    },
    // Handle event click (for deletion)
    eventClick: function(info) {
      // Prompt the user to confirm deletion
      if (confirm(`Are you sure you want to delete the event "${info.event.title}"?`)) {
        // Remove the event from the calendar
        info.event.remove();
    
        // Send a DELETE request to the backend
        fetch(`/api/events/${info.event.id}`, { // Use the actual event ID
          method: 'DELETE',          
        })

        .then(response => response.json())
        .then(data => {
          if (data.message) {
            alert(data.message);
          } else {
            alert('Error deleting event from the database.');
          }
        })
        .catch(error => {
          console.error('Error:', error);
          alert('Failed to connect to the server.');
        });
      }
    },
    
    // Handle event creation
    customButtons: {
      addEventButton: {
        text: 'add event...',
        click: function() {
          var dateStr = prompt('Enter a date in YYYY-MM-DD format');
          var title = prompt('Enter the name of your event')
          var start = new Date(dateStr + 'T00:00:00'); // will be in local time

          if (!isNaN(start.valueOf())) { // valid?
            // Save the event to the database
            fetch('/api/events', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            title: title,
            start: dateStr
          }),
        })
        .then(response => response.json())
        .then(data => {
          if (data.message) {
            alert(data.message);

            // Dynamically add the new event to the calendar
            calendar.addEvent({
              title: title,
              start: dateStr, // Use the same date string sent to the backend
            });
          } else {
            alert('Error adding event to the database.');
          }
        })
        .catch(error => {
          console.error('Error:', error);
          alert('Failed to connect to the server.');
        });
      } else {
        alert('Invalid date.');
      }
    }
  }
},

    // Handle event drop from to-do list
    drop: function(info) {
      console.log('To-do item dropped:', info.draggedEl);

      // Save the dropped event to the backend
      fetch('/api/events', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: info.draggedEl.getAttribute('data-title'), // Get the title from the dragged element
          start: info.dateStr // Use the date where the event was dropped
        }),
      })
      .then(response => response.json())
      .then(data => {
        if (data.message) {
          alert(data.message);
        } else {
          alert('Error saving event to the database.');
        }
      })
      .catch(error => {
        console.error('Error:', error);
        alert('Failed to connect to the server.');
      });
    }
  });
  calendar.render();
  // Add new to-do list items
  window.newElement = function() {
    const inputValue = document.getElementById("myInput").value;

    if (inputValue === "") {
      alert("You must write something!");
      return;
    }

    const li = document.createElement("li");
    li.textContent = inputValue;
    li.setAttribute("data-title", inputValue); // Set a data attribute for FullCalendar
    
    // Create a delete button
    const deleteBtn = document.createElement("span");
    deleteBtn.textContent = "X"; // Text for the delete button
    deleteBtn.className = "delete-btn"; // Add a class for styling
    deleteBtn.onclick = function() {
    li.remove(); // Remove the list item when the delete button is clicked
    };
      // Prevent dragging when clicking the delete button
    deleteBtn.addEventListener("click", function(event) {
    event.stopPropagation(); // Prevent the drag event from being triggered
    li.remove(); // Remove the list item when the delete button is clicked
  });
    li.appendChild(deleteBtn);

    document.getElementById("myUL").appendChild(li);

    document.getElementById("myInput").value = ""; // Clear the input field
  };
}); 
let currentDate = new Date()
 
const updateCalendar = () => {
    const currentYear = currentDate.getFullYear();
    const currentMonth = currentDate.getMonth();
 
    const firstDay = new Date(currentYear, currentMonth, 0);
    const lastDay = new Date(currentYear, currentMonth + 1, 0);
    const totalDays = lastDay.getDate();
    const firstDayIndex = firstDay.getDay();
    const lastDayIndex = lastDay.getDay();
 
    const monthYearString = currentDate.toLocaleString
    ('default', {month:'long', year:'numeric'});
    monthYearElement.textContent = monthYearString;
 
    let datesHTML = '';
 
    for(let i = firstDayIndex; i > 0; i--) {
        const prevDate = new Date(currentYear, currentMonth, 0-i+1);
        datesHTML += `<div class = "date inactive">${prevDate.getDate()}</div>`;
     }
 
    for(let i = 1; i <= totalDays; i++){
        const date = new Date(currentYear, currentMonth, i);
        const activeClass = date.toDateString() === new Date().toDateString() ? 'active' : '';
        datesHTML += `<div class = 'date ${activeClass}'>${i}</div>`;
     }
 
    for(let i = 1; i <= 7 - lastDayIndex; i++){
        const nextDate = new Date(currentYear, currentMonth+1, i);
        datesHTML += `<div class = "date inactive">${nextDate.getDate()}</div>`;
     }
     datesElement.innerHTML = datesHTML;
 }
 
prevBtn.addEventListener('click', () => {
    currentDate.setMonth(currentDate.getMonth()-1);
    updateCalendar();
})
 
nextBtn.addEventListener('click', () => {
    currentDate.setMonth(currentDate.getMonth()+1);
    updateCalendar();
})