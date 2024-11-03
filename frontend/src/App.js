import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [backendData, setBackendData] = useState('');
  const [link, setLink] = useState('');

  const fetchBackendData = async () => {
    if (!link) {
      setBackendData('Please enter a link');
      return;
    }

    try {
      console.log('API URL:', process.env.REACT_APP_API_URL);
      const response = await axios.get(`${process.env.REACT_APP_API_URL}/`, {
        params: { link: link }
      });
      setBackendData(JSON.stringify(response.data));
    } catch (error) {
      console.error('Error fetching data:', error);
      setBackendData('Error fetching data');
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    fetchBackendData();
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      fetchBackendData();
    }
  };

  return (
    <div className="App">
      <h1>Ghost AI</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={link}
          onChange={(e) => setLink(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Enter link here"
        />
        <button type="submit">Submit</button>
      </form>
      <p>{backendData}</p>
    </div>
  );
}

export default App;