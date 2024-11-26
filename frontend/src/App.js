import React, { useState } from 'react';

function App() {
  const [file, setFile] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    
    // Validate file type
    if (selectedFile && !selectedFile.name.endsWith('.zip')) {
      setError('Please select a ZIP file');
      setFile(null);
      return;
    }

    // Validate file size (e.g., 50MB limit)
    if (selectedFile && selectedFile.size > 70 * 1024 * 1024) {
      setError('File size must be less than 50MB');
      setFile(null);
      return;
    }

    setFile(selectedFile);
    setError(null);
    setUploadProgress(0);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!file) {
      setError('Please select a file');
      return;
    }

    setAnalyzing(true);
    setError(null);
    setUploadProgress(0);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8080/analyze', {  // Make sure this URL is correct
        method: 'POST',
        body: formData,
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);   

          setUploadProgress(percentCompleted);
        },
      });

      if (!response.ok)   
 {
        const errorData = await response.json(); // Try to parse error details from the response
        const errorMessage = errorData.detail || 'Server error occurred'; 
        throw new Error(errorMessage); 
      }

      const data = await response.json();
      console.log('Response data:', data); // Log the response data for debugging

      if (!data.results) { 
        throw new Error('Invalid response format from server');
      }

      setResults(data.results);
    } catch (err) {
      console.error('Upload error:', err);
      setError(err.message || 'Failed to upload and analyze the file.'); 
      setResults(null);
    } finally {
      setAnalyzing(false);
      setUploadProgress(0);
    }
  };

  return (
    <div className="App" style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      <h1 style={{ textAlign: 'center', marginBottom: '30px' }}>Code Project Analyzer</h1>

      <div style={{
        border: '2px dashed #ccc',
        padding: '20px',
        borderRadius: '8px',
        marginBottom: '20px'
      }}>
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '20px' }}>
            <input
              type="file"
              accept=".zip"
              onChange={handleFileChange}
              style={{ marginBottom: '10px', display: 'block' }}
            />
            <small style={{ color: '#666' }}>
              Upload your project as a ZIP file (max 50MB)
            </small>
          </div>

          {uploadProgress > 0 && uploadProgress < 100 && (
            <div style={{ marginBottom: '20px' }}>
              <div style={{
                width: '100%',
                height: '20px',
                backgroundColor: '#f0f0f0',
                borderRadius: '10px',
                overflow: 'hidden'
              }}>
                <div style={{
                  width: `${uploadProgress}%`,
                  height: '100%',
                  backgroundColor: '#007bff',
                  transition: 'width 0.3s ease-in-out'
                }} />
              </div>
              <small style={{ color: '#666' }}>{uploadProgress}% uploaded</small>
            </div>
          )}

          <button
            type="submit"
            disabled={analyzing || !file}
            style={{
              padding: '10px 20px',
              backgroundColor: analyzing ? '#ccc' : '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: analyzing ? 'not-allowed' : 'pointer'
            }}
          >
            {analyzing ? 'Analyzing...' : 'Analyze Project'}
          </button>
        </form>
      </div>

      {error && (
        <div style={{
          padding: '10px',
          backgroundColor: '#ffebee',
          color: '#c62828',
          borderRadius: '4px',
          marginBottom: '20px'
        }}>
          <strong>Error: </strong>{error}
        </div>
      )}

      {}
      {results && (
        <div style={{ marginTop: '30px' }}>
          {}
        </div>
      )}
    </div>
  );
}

export default App;


