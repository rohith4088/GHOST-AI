import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [file, setFile] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    
    if (selectedFile && !selectedFile.name.endsWith('.zip')) {
      setError('Please select a ZIP file');
      setFile(null);
      return;
    }

    if (selectedFile && selectedFile.size > 50 * 1024 * 1024) {
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
    setResults(null);
    setUploadProgress(0);

    const formData = new FormData();
    formData.append('file', file);

    try {
      console.log('Sending request to server...');
      const response = await axios.post('http://localhost:8080/analyze', formData, {
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          setUploadProgress(percentCompleted);
        },
        // Increase timeout for large files
        timeout: 180000, // 3 minutes
      });

      console.log('Server response:', response.data);
      
      // Store the raw response data - much simpler approach
      setResults(response.data);
    } catch (err) {
      console.error('Upload error:', err);
      console.error('Error response:', err.response);
      
      let errorMessage;
      if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      } else if (err.response?.data?.message) {
        errorMessage = err.response.data.message;
      } else if (err.message) {
        errorMessage = err.message;
      } else {
        errorMessage = 'Failed to analyze file';
      }
      
      setError(`Error: ${errorMessage}`);
      setResults(null);
    } finally {
      setAnalyzing(false);
      setUploadProgress(0);
    }
  };

  const renderAnalysisSection = () => {
    if (!results || !results.project_analysis) {
      console.log('No valid analysis data:', results);
      return (
        <div style={{ 
          marginTop: '32px',
          background: 'white',
          borderRadius: '16px',
          padding: '32px',
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
        }}>
          <h2 style={{ 
            marginBottom: '24px', 
            color: '#1f2937', 
            fontSize: '1.5rem', 
            fontWeight: 600 
          }}>
            Analysis Results
          </h2>
          <div style={{
            padding: '16px',
            background: '#f0f9ff',
            borderRadius: '8px',
            borderLeft: '4px solid #3b82f6',
          }}>
            <p style={{ color: '#4b5563', lineHeight: '1.6' }}>
              The analysis data was received but couldn't be properly displayed. 
              Please check the developer console for more information.
            </p>
            <pre style={{
              marginTop: '16px',
              padding: '12px',
              background: '#f1f5f9',
              borderRadius: '6px',
              fontSize: '0.85rem',
              overflowX: 'auto'
            }}>
              {JSON.stringify(results, null, 2)}
            </pre>
          </div>
        </div>
      );
    }
    
    // Extract the actual analysis data from the nested structure
    const projectData = results.project_analysis?.project_analysis || {};
    
    // Create an analysis object with normalized structure
    const analysis = {
      "Overall Project Architecture Overview": {
        "Description": 
          projectData.details?.raw?.content ||
          projectData.architecture_summary ||
          "No project overview available"
      },
      "Code Organization and Modularity Assessment": {
        "Assessment": "No assessment available",
        "Score": null
      },
      "Design Patterns and Structural Insights": {
        "Assessment": "No assessment available",
        "Score": null
      },
      "Long-term Maintainability Assessment": {
        "Assessment": "No assessment available",
        "Score": null
      },
      "Recommendations": {
        "Key Takeaways": [],
        "Action Items": []
      }
    };
    
    // Try to extract key takeaways and action items
    if (typeof projectData.details?.raw?.content === 'string') {
      try {
        // Look for JSON content in the raw text
        const jsonMatches = projectData.details.raw.content.match(/```json([\s\S]*?)```/);
        if (jsonMatches && jsonMatches[1]) {
          const jsonContent = JSON.parse(jsonMatches[1].trim());
          
          // Extract insights from the parsed JSON
          if (jsonContent.analysisResults) {
            const results = jsonContent.analysisResults;
            
            // Extract key takeaways from various sections
            const takeaways = [];
            const actionItems = [];
            
            // Extract implications as takeaways
            Object.keys(results).forEach(key => {
              if (results[key]?.implications) {
                results[key].implications.forEach(imp => {
                  if (imp) takeaways.push(imp);
                });
              }
            });
            
            // Add some generic action items based on takeaways
            if (takeaways.length > 0) {
              actionItems.push("Review project structure and establish clear architecture");
              actionItems.push("Implement proper modularity and separation of concerns");
              actionItems.push("Define clear entry points and component interfaces");
            }
            
            analysis.Recommendations["Key Takeaways"] = takeaways.slice(0, 5);
            analysis.Recommendations["Action Items"] = actionItems;
            
            // Update section assessments if available
            if (results.codeOrganizationAndModularityAssessment?.description) {
              analysis["Code Organization and Modularity Assessment"].Assessment = 
                results.codeOrganizationAndModularityAssessment.description;
            }
            
            if (results.designPatternsAndStructuralInsights?.description) {
              analysis["Design Patterns and Structural Insights"].Assessment = 
                results.designPatternsAndStructuralInsights.description;
            }
            
            if (results.longTermMaintainabilityAssessment?.description) {
              analysis["Long-term Maintainability Assessment"].Assessment = 
                results.longTermMaintainabilityAssessment.description;
            }
          }
        }
      } catch (e) {
        console.error("Error parsing embedded JSON content:", e);
      }
    }
    
    return (
      <div style={{ 
        marginTop: '32px',
        background: 'white',
        borderRadius: '16px',
        padding: '32px',
        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
      }}>
        <h2 style={{ 
          marginBottom: '24px', 
          color: '#1f2937', 
          fontSize: '1.5rem', 
          fontWeight: 600 
        }}>
          Analysis Results
        </h2>

        {/* Project Overview */}
        <div style={{ marginBottom: '32px' }}>
          <h3 style={{ 
            fontSize: '1.2rem', 
            marginBottom: '16px', 
            color: '#3b82f6',
            borderBottom: '2px solid #e5e7eb',
            paddingBottom: '8px'
          }}>
            Project Overview
          </h3>
          <p style={{ color: '#4b5563', lineHeight: '1.6' }}>
            {analysis["Overall Project Architecture Overview"]?.Description || 'No overview available'}
          </p>
        </div>

        {/* Key Recommendations */}
        <div style={{ marginBottom: '32px' }}>
          <h3 style={{ 
            fontSize: '1.2rem', 
            marginBottom: '16px', 
            color: '#3b82f6',
            borderBottom: '2px solid #e5e7eb',
            paddingBottom: '8px'
          }}>
            Key Recommendations
          </h3>
          <div style={{ 
            display: 'grid', 
            gap: '16px', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))'
          }}>
            {(analysis.Recommendations?.["Key Takeaways"] || []).map((item, index) => (
              <div key={index} style={{
                padding: '16px',
                background: '#f8fafc',
                borderRadius: '8px',
                borderLeft: '4px solid #3b82f6',
                transition: 'all 0.2s ease'
              }}>
                <div style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: '12px',
                  color: '#1f2937'
                }}>
                  <svg 
                    style={{ 
                      flexShrink: 0,
                      width: '20px', 
                      height: '20px', 
                      color: '#3b82f6' 
                    }} 
                    fill="none" 
                    stroke="currentColor" 
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  <span>{item}</span>
                </div>
              </div>
            ))}
            
            {analysis.Recommendations?.["Key Takeaways"].length === 0 && (
              <div style={{
                padding: '16px',
                background: '#f8fafc',
                borderRadius: '8px',
                borderLeft: '4px solid #f59e0b',
              }}>
                <div style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: '12px',
                  color: '#1f2937'
                }}>
                  <svg 
                    style={{ 
                      flexShrink: 0,
                      width: '20px', 
                      height: '20px', 
                      color: '#f59e0b' 
                    }} 
                    fill="none" 
                    stroke="currentColor" 
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  <span>No key recommendations available for this project</span>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Action Items */}
        <div style={{ marginBottom: '32px' }}>
          <h3 style={{ 
            fontSize: '1.2rem', 
            marginBottom: '16px', 
            color: '#3b82f6',
            borderBottom: '2px solid #e5e7eb',
            paddingBottom: '8px'
          }}>
            Action Items
          </h3>
          <ul style={{ listStyle: 'none', paddingLeft: 0 }}>
            {(analysis.Recommendations?.["Action Items"] || []).map((item, index) => (
              <li key={index} style={{ 
                padding: '12px 0',
                borderBottom: '1px solid #e5e7eb',
                display: 'flex',
                alignItems: 'center',
                gap: '12px'
              }}>
                <svg 
                  style={{ 
                    flexShrink: 0,
                    width: '16px', 
                    height: '16px', 
                    color: '#3b82f6' 
                  }} 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                </svg>
                <span style={{ color: '#374151' }}>{item}</span>
              </li>
            ))}
            
            {analysis.Recommendations?.["Action Items"].length === 0 && (
              <li style={{ 
                padding: '12px 0',
                display: 'flex',
                alignItems: 'center',
                gap: '12px'
              }}>
                <svg 
                  style={{ 
                    flexShrink: 0,
                    width: '16px', 
                    height: '16px', 
                    color: '#f59e0b' 
                  }} 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span style={{ color: '#374151' }}>No action items available</span>
              </li>
            )}
          </ul>
        </div>

        {/* Technical Assessments */}
        <div style={{ 
          display: 'grid', 
          gap: '24px', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))'
        }}>
          {/* Code Organization */}
          <div style={{ 
            padding: '24px', 
            background: '#f8fafc', 
            borderRadius: '12px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
          }}>
            <h4 style={{ 
              fontSize: '1.1rem', 
              marginBottom: '12px', 
              color: '#3b82f6',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <svg 
                style={{ width: '20px', height: '20px' }} 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
              Code Organization
            </h4>
            <p style={{ color: '#4b5563', lineHeight: '1.6' }}>
              {analysis["Code Organization and Modularity Assessment"]?.Assessment || 'No assessment available'}
            </p>
            {analysis["Code Organization and Modularity Assessment"]?.Score && (
              <div style={{ marginTop: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ color: '#6b7280', fontSize: '0.9rem' }}>Score:</span>
                <span style={{ 
                  fontWeight: 600, 
                  color: '#3b82f6' 
                }}>
                  {analysis["Code Organization and Modularity Assessment"]?.Score}/10
                </span>
              </div>
            )}
          </div>

          {/* Design Patterns */}
          <div style={{ 
            padding: '24px', 
            background: '#f8fafc', 
            borderRadius: '12px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
          }}>
            <h4 style={{ 
              fontSize: '1.1rem', 
              marginBottom: '12px', 
              color: '#3b82f6',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <svg 
                style={{ width: '20px', height: '20px' }} 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
              Design Patterns
            </h4>
            <p style={{ color: '#4b5563', lineHeight: '1.6' }}>
              {analysis["Design Patterns and Structural Insights"]?.Assessment || 'No assessment available'}
            </p>
            {analysis["Design Patterns and Structural Insights"]?.Score && (
              <div style={{ marginTop: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ color: '#6b7280', fontSize: '0.9rem' }}>Score:</span>
                <span style={{ 
                  fontWeight: 600, 
                  color: '#3b82f6' 
                }}>
                  {analysis["Design Patterns and Structural Insights"]?.Score}/10
                </span>
              </div>
            )}
          </div>

          {/* Maintainability */}
          <div style={{ 
            padding: '24px', 
            background: '#f8fafc', 
            borderRadius: '12px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
          }}>
            <h4 style={{ 
              fontSize: '1.1rem', 
              marginBottom: '12px', 
              color: '#3b82f6',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <svg 
                style={{ width: '20px', height: '20px' }} 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Maintainability
            </h4>
            <p style={{ color: '#4b5563', lineHeight: '1.6' }}>
              {analysis["Long-term Maintainability Assessment"]?.Assessment || 'No assessment available'}
            </p>
            {analysis["Long-term Maintainability Assessment"]?.Score && (
              <div style={{ marginTop: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ color: '#6b7280', fontSize: '0.9rem' }}>Score:</span>
                <span style={{ 
                  fontWeight: 600, 
                  color: '#3b82f6' 
                }}>
                  {analysis["Long-term Maintainability Assessment"]?.Score}/10
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Raw Response for Debugging */}
        <div style={{ marginTop: '32px' }}>
          <details>
            <summary style={{ 
              cursor: 'pointer',
              color: '#6b7280',
              padding: '12px',
              background: '#f1f5f9',
              borderRadius: '6px',
              fontSize: '0.9rem',
              fontWeight: 500
            }}>
              View Raw Response Data
            </summary>
            <pre style={{
              marginTop: '12px',
              padding: '12px',
              background: '#f1f5f9',
              borderRadius: '6px',
              fontSize: '0.85rem',
              overflowX: 'auto'
            }}>
              {JSON.stringify(results, null, 2)}
            </pre>
          </details>
        </div>
      </div>
    );
  };

  return (
    <div className="App" style={{ 
      padding: '40px 20px',
      maxWidth: '1200px',
      margin: '0 auto',
      minHeight: '100vh',
      fontFamily: "'Inter', sans-serif",
      background: 'linear-gradient(45deg, #f3f4f6 0%, #f9fafb 100%)'
    }}>
      <h1 style={{ 
        textAlign: 'center',
        marginBottom: '40px',
        fontSize: '2.5rem',
        fontWeight: 700,
        color: '#1f2937',
        letterSpacing: '-0.025em'
      }}>
        <span style={{ color: '#3b82f6' }}>Code</span> Analyzer
      </h1>

      <div style={{
        background: 'white',
        borderRadius: '16px',
        padding: '32px',
        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        marginBottom: '24px',
        transition: 'transform 0.2s ease',
        ':hover': {
          transform: 'translateY(-2px)'
        }
      }}>
        <form onSubmit={handleSubmit} style={{ position: 'relative' }}>
          <div style={{ 
            marginBottom: '24px',
            textAlign: 'center'
          }}>
            <label style={{
              display: 'inline-flex',
              flexDirection: 'column',
              alignItems: 'center',
              cursor: !analyzing ? 'pointer' : 'default',
              opacity: analyzing ? 0.7 : 1
            }}>
              <input
                type="file"
                accept=".zip"
                onChange={handleFileChange}
                style={{ display: 'none' }}
                disabled={analyzing}
              />
              <div style={{
                width: '80px',
                height: '80px',
                borderRadius: '50%',
                background: '#e0e7ff',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: '16px',
                transition: 'all 0.2s ease'
              }}>
                <svg 
                  style={{ 
                    width: '32px',
                    height: '32px',
                    color: '#3b82f6' 
                  }} 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
              </div>
              <div style={{ marginBottom: '8px' }}>
                {file ? (
                  <span style={{ color: '#1f2937', fontWeight: 500 }}>
                    {file.name}
                  </span>
                ) : (
                  <>
                    <span style={{ color: '#3b82f6', fontWeight: 500 }}>Choose file</span>
                    <span style={{ color: '#6b7280' }}> or drag and drop</span>
                  </>
                )}
              </div>
              <small style={{ color: '#6b7280', fontSize: '0.875rem' }}>
                ZIP format, up to 50MB
              </small>
            </label>
          </div>

          {uploadProgress > 0 && uploadProgress < 100 && (
            <div style={{ 
              marginBottom: '24px',
              position: 'relative'
            }}>
              <div style={{
                height: '8px',
                background: '#e5e7eb',
                borderRadius: '4px',
                overflow: 'hidden'
              }}>
                <div style={{
                  width: `${uploadProgress}%`,
                  height: '100%',
                  background: 'linear-gradient(90deg, #3b82f6 0%, #60a5fa 100%)',
                  transition: 'width 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                  borderRadius: '4px'
                }} />
              </div>
              <div style={{
                position: 'absolute',
                right: 0,
                top: '12px',
                color: '#6b7280',
                fontSize: '0.875rem'
              }}>
                {uploadProgress}%
              </div>
            </div>
          )}

          {error && (
            <div style={{
              padding: '12px 16px',
              background: '#fee2e2',
              color: '#dc2626',
              borderRadius: '8px',
              marginBottom: '24px',
              fontSize: '0.9rem',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <svg 
                style={{ width: '20px', height: '20px' }} 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>{error}</span>
            </div>
          )}

          <div style={{ textAlign: 'center' }}>
            <button
              type="submit"
              disabled={analyzing || !file}
              style={{
                padding: '12px 24px',
                background: analyzing ? '#c7d2fe' : 'linear-gradient(90deg, #3b82f6 0%, #60a5fa 100%)',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: analyzing ? 'not-allowed' : 'pointer',
                fontWeight: 600,
                fontSize: '1rem',
                transition: 'all 0.2s ease',
                ':hover': !analyzing && {
                  transform: 'scale(1.05)',
                  boxShadow: '0 4px 6px -1px rgba(59, 130, 246, 0.3)'
                }
              }}
            >
              {analyzing ? (
                <>
                  <span style={{ verticalAlign: 'middle' }}>Analyzing...</span>
                  <svg
                    style={{
                      width: '20px',
                      height: '20px',
                      marginLeft: '8px',
                      verticalAlign: 'middle',
                      animation: 'spin 1s linear infinite'
                    }}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                </>
              ) : (
                'Analyze Project'
              )}
            </button>
          </div>
        </form>
      </div>

      {results && renderAnalysisSection()}

      {/* Add a keyframes style for the spinner animation */}
      <style dangerouslySetInnerHTML={{
        __html: `
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
        `
      }} />
    </div>
  );
}

export default App;