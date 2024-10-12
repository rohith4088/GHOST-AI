import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [backendData, setBackendData] = useState('');

  const fetchBackendData = async () => {
    try {
      console.log('API URL:', process.env.REACT_APP_API_URL); 
      const response = await axios.get(`${process.env.REACT_APP_API_URL}/`);
      setBackendData(JSON.stringify(response.data));
    } catch (error) {
      console.error('Error fetching data:', error);
      setBackendData('Error fetching data');
    }
  };

  return (
    <div className="App">
      <h1>My Frontend App</h1>
      <button onClick={fetchBackendData}>Fetch Data from Backend</button>
      <p>{backendData}</p>
    </div>
  );
}

export default App;