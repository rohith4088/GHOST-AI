import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';  

const root = ReactDOM.createRoot(document.getElementById('root'));  // Reference to the root element in HTML
root.render(
  <React.StrictMode>
    <App />  {/* Render the App component inside the root */}
  </React.StrictMode>
);
