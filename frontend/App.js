// Function to make API calls
function testApiCalls() {
    // Backend service
    const backendUrl = 'http://localhost:8080';
    
    fetch(backendUrl)
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        console.log('Backend call successful!');
        console.log('Response:', JSON.stringify(data, null, 2));
        
        // Frontend service
        const frontendUrl = 'http://localhost:3000';
        
        fetch(frontendUrl)
          .then(response => {
            if (!response.ok) {
              throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.text();
          })
          .then(html => {
            console.log('Frontend HTML:');
            console.log(html.substring(0, 500)); // Display first 500 characters
          })
          .catch(error => {
            console.error('There was a problem with the frontend call:', error.message);
          });
      })
      .catch(error => {
        console.error('There was a problem with the backend call:', error.message);
      });
  }
  
  // Call the function when the page loads
  document.addEventListener('DOMContentLoaded', testApiCalls);
  