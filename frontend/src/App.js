// import React, { useState } from 'react';
// import axios from 'axios';

// function App() {
//   const [file, setFile] = useState(null);
//   const [analyzing, setAnalyzing] = useState(false);
//   const [results, setResults] = useState(null);
//   const [error, setError] = useState(null);
//   const [uploadProgress, setUploadProgress] = useState(0);

//   const handleFileChange = (event) => {
//     const selectedFile = event.target.files[0];
    
//     if (selectedFile && !selectedFile.name.endsWith('.zip')) {
//       setError('Please select a ZIP file');
//       setFile(null);
//       return;
//     }

//     if (selectedFile && selectedFile.size > 50 * 1024 * 1024) {
//       setError('File size must be less than 50MB');
//       setFile(null);
//       return;
//     }

//     setFile(selectedFile);
//     setError(null);
//     setUploadProgress(0);
//   };

//   const handleSubmit = async (event) => {
//     event.preventDefault();
//     if (!file) {
//       setError('Please select a file');
//       return;
//     }

//     setAnalyzing(true);
//     setError(null);
//     setUploadProgress(0);

//     const formData = new FormData();
//     formData.append('file', file);

//     try {
//       const response = await axios.post('http://localhost:8080/analyze', formData, {
//         onUploadProgress: (progressEvent) => {
//           const percentCompleted = Math.round(
//             (progressEvent.loaded * 100) / progressEvent.total
//           );
//           setUploadProgress(percentCompleted);
//         },
//       });

//       if (response.data.results) {
//         setResults(response.data.results);
//       } else {
//         throw new Error('Invalid response format from server');
//       }
//     } catch (err) {
//       console.error('Upload error:', err);
//       setError(err.response?.data?.detail || err.message || 'Failed to analyze file');
//       setResults(null);
//     } finally {
//       setAnalyzing(false);
//       setUploadProgress(0);
//     }
//   };

//   return (
//     <div className="App" style={{ 
//       padding: '40px 20px',
//       maxWidth: '800px',
//       margin: '0 auto',
//       minHeight: '100vh',
//       fontFamily: "'Inter', sans-serif",
//       background: 'linear-gradient(45deg, #f3f4f6 0%, #f9fafb 100%)'
//     }}>
//       <h1 style={{ 
//         textAlign: 'center',
//         marginBottom: '40px',
//         fontSize: '2.5rem',
//         fontWeight: 700,
//         color: '#1f2937',
//         letterSpacing: '-0.025em'
//       }}>
//         <span style={{ color: '#3b82f6' }}>Code</span> Analyzer
//       </h1>

//       <div style={{
//         background: 'white',
//         borderRadius: '16px',
//         padding: '32px',
//         boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
//         marginBottom: '24px',
//         transition: 'transform 0.2s ease',
//         ':hover': {
//           transform: 'translateY(-2px)'
//         }
//       }}>
//         <form onSubmit={handleSubmit} style={{ position: 'relative' }}>
//           <div style={{ 
//             marginBottom: '24px',
//             textAlign: 'center'
//           }}>
//             <label style={{
//               display: 'inline-flex',
//               flexDirection: 'column',
//               alignItems: 'center',
//               cursor: !analyzing ? 'pointer' : 'default',
//               opacity: analyzing ? 0.7 : 1
//             }}>
//               <input
//                 type="file"
//                 accept=".zip"
//                 onChange={handleFileChange}
//                 style={{ display: 'none' }}
//                 disabled={analyzing}
//               />
//               <div style={{
//                 width: '80px',
//                 height: '80px',
//                 borderRadius: '50%',
//                 background: '#e0e7ff',
//                 display: 'flex',
//                 alignItems: 'center',
//                 justifyContent: 'center',
//                 marginBottom: '16px',
//                 transition: 'all 0.2s ease'
//               }}>
//                 <svg 
//                   style={{ 
//                     width: '32px',
//                     height: '32px',
//                     color: '#3b82f6' 
//                   }} 
//                   fill="none" 
//                   stroke="currentColor" 
//                   viewBox="0 0 24 24"
//                 >
//                   <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
//                 </svg>
//               </div>
//               <div style={{ marginBottom: '8px' }}>
//                 {file ? (
//                   <span style={{ color: '#1f2937', fontWeight: 500 }}>
//                     {file.name}
//                   </span>
//                 ) : (
//                   <>
//                     <span style={{ color: '#3b82f6', fontWeight: 500 }}>Choose file</span>
//                     <span style={{ color: '#6b7280' }}> or drag and drop</span>
//                   </>
//                 )}
//               </div>
//               <small style={{ color: '#6b7280', fontSize: '0.875rem' }}>
//                 ZIP format, up to 50MB
//               </small>
//             </label>
//           </div>

//           {uploadProgress > 0 && uploadProgress < 100 && (
//             <div style={{ 
//               marginBottom: '24px',
//               position: 'relative'
//             }}>
//               <div style={{
//                 height: '8px',
//                 background: '#e5e7eb',
//                 borderRadius: '4px',
//                 overflow: 'hidden'
//               }}>
//                 <div style={{
//                   width: `${uploadProgress}%`,
//                   height: '100%',
//                   background: 'linear-gradient(90deg, #3b82f6 0%, #60a5fa 100%)',
//                   transition: 'width 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
//                   borderRadius: '4px'
//                 }} />
//               </div>
//               <div style={{
//                 position: 'absolute',
//                 right: 0,
//                 top: '12px',
//                 color: '#6b7280',
//                 fontSize: '0.875rem'
//               }}>
//                 {uploadProgress}%
//               </div>
//             </div>
//           )}

//           <div style={{ textAlign: 'center' }}>
//             <button
//               type="submit"
//               disabled={analyzing || !file}
//               style={{
//                 padding: '12px 24px',
//                 background: analyzing ? '#c7d2fe' : 'linear-gradient(90deg, #3b82f6 0%, #60a5fa 100%)',
//                 color: 'white',
//                 border: 'none',
//                 borderRadius: '8px',
//                 cursor: analyzing ? 'not-allowed' : 'pointer',
//                 fontWeight: 600,
//                 fontSize: '1rem',
//                 transition: 'all 0.2s ease',
//                 ':hover': !analyzing && {
//                   transform: 'scale(1.05)',
//                   boxShadow: '0 4px 6px -1px rgba(59, 130, 246, 0.3)'
//                 }
//               }}
//             >
//               {analyzing ? (
//                 <>
//                   <span style={{ verticalAlign: 'middle' }}>Analyzing...</span>
//                   <svg
//                     style={{
//                       width: '20px',
//                       height: '20px',
//                       marginLeft: '8px',
//                       verticalAlign: 'middle',
//                       animation: 'spin 1s linear infinite'
//                     }}
//                     fill="none"
//                     stroke="currentColor"
//                     viewBox="0 0 24 24"
//                   >
//                     <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
//                   </svg>
//                 </>
//               ) : (
//                 'Analyze Project'
//               )}
//             </button>
//           </div>
//         </form>
//       </div>

//       {error && (
//         <div style={{
//           padding: '16px',
//           background: '#fee2e2',
//           color: '#dc2626',
//           borderRadius: '8px',
//           marginBottom: '24px',
//           display: 'flex',
//           alignItems: 'center',
//           gap: '12px'
//         }}>
//           <svg 
//             style={{ 
//               flexShrink: 0,
//               width: '20px',
//               height: '20px' 
//             }} 
//             fill="none" 
//             stroke="currentColor" 
//             viewBox="0 0 24 24"
//           >
//             <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
//           </svg>
//           <div>
//             <strong style={{ fontWeight: 500 }}>Error:</strong> {error}
//           </div>
//         </div>
//       )}

//       {results && (
//         <div style={{ 
//           marginTop: '32px',
//           background: 'white',
//           borderRadius: '16px',
//           padding: '32px',
//           boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
//         }}>
//           <h2 style={{ marginBottom: '24px', color: '#1f2937', fontSize: '1.5rem', fontWeight: 600 }}>
//             Analysis Results
//           </h2>
//           {/* Add your results display here */}
//         </div>
//       )}

//       <style>{`
//         @keyframes spin {
//           from { transform: rotate(0deg); }
//           to { transform: rotate(360deg); }
//         }
        
//         @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
//       `}</style>
//     </div>
//   );
// }

// export default App;


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
      
      // More flexible parsing approach
      if (response.data) {
        try {
          let analysisContent;
          let projectAnalysis;
          
          // Check for different possible response structures
          if (response.data.results?.project_analysis?.content) {
            // Original expected structure
            analysisContent = response.data.results.project_analysis.content;
          } else if (response.data.project_analysis?.content) {
            // Alternative structure without 'results' wrapper
            analysisContent = response.data.project_analysis.content;
          } else if (response.data.content) {
            // Direct content property
            analysisContent = response.data.content;
          } else if (typeof response.data === 'string') {
            // Response is directly the content string
            analysisContent = response.data;
          } else if (response.data.results && typeof response.data.results === 'object') {
            // Results is already the analysis object
            projectAnalysis = response.data.results;
          } else if (typeof response.data === 'object') {
            // Response data is directly the analysis object
            projectAnalysis = response.data;
          }
          
          // Parse the content if it's a string, otherwise use the object directly
          if (analysisContent) {
            // Try to parse if it's a string
            if (typeof analysisContent === 'string') {
              try {
                projectAnalysis = {
                  parsed: JSON.parse(analysisContent)
                };
              } catch (jsonParseError) {
                console.error('JSON parse error:', jsonParseError);
                // If it fails, maybe it's already a JSON object stringified multiple times
                try {
                  projectAnalysis = {
                    parsed: JSON.parse(JSON.stringify(analysisContent))
                  };
                } catch (secondParseError) {
                  console.error('Second parse attempt failed:', secondParseError);
                  projectAnalysis = {
                    parsed: { error: "Could not parse analysis content" }
                  };
                }
              }
            } else if (typeof analysisContent === 'object') {
              // It's already an object
              projectAnalysis = {
                parsed: analysisContent
              };
            }
          }
          
          // Set the results with whatever we managed to parse
          if (projectAnalysis) {
            setResults({
              project_analysis: projectAnalysis
            });
          } else {
            throw new Error('Could not extract analysis data from server response');
          }
        } catch (parseError) {
          console.error('Parse error:', parseError);
          console.error('Response data:', response.data);
          throw new Error(`Failed to parse analysis content: ${parseError.message}`);
        }
      } else {
        console.error('Empty response from server');
        throw new Error('Empty response from server');
      }
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
    if (!results?.project_analysis?.parsed) {
      console.log('No parsed analysis data:', results);
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

    const analysis = results.project_analysis.parsed;
    
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

        {/* Performance Metrics */}
        {analysis["Performance Metrics"] && (
          <div style={{ marginTop: '32px' }}>
            <h3 style={{ 
              fontSize: '1.2rem', 
              marginBottom: '16px', 
              color: '#3b82f6',
              borderBottom: '2px solid #e5e7eb',
              paddingBottom: '8px'
            }}>
              Performance Metrics
            </h3>
            <div style={{
              display: 'grid',
              gap: '16px',
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))'
            }}>
              {Object.entries(analysis["Performance Metrics"]).map(([key, value], index) => (
                <div key={index} style={{
                  background: '#f8fafc',
                  padding: '16px',
                  borderRadius: '8px',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  textAlign: 'center'
                }}>
                  <div style={{
                    width: '60px',
                    height: '60px',
                    borderRadius: '50%',
                    background: '#e0e7ff',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    marginBottom: '12px'
                  }}>
                    <span style={{
                      fontSize: '1.5rem',
                      fontWeight: 700,
                      color: '#3b82f6'
                    }}>
                      {typeof value === 'number' ? value : '-'}
                    </span>
                  </div>
                  <h5 style={{
                    margin: 0,
                    color: '#4b5563',
                    fontSize: '0.9rem'
                  }}>
                    {key.replace(/([A-Z])/g, ' $1').trim()}
                  </h5>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Security Analysis */}
        {analysis["Security Analysis"] && (
          <div style={{ marginTop: '32px' }}>
            <h3 style={{ 
              fontSize: '1.2rem', 
              marginBottom: '16px', 
              color: '#3b82f6',
              borderBottom: '2px solid #e5e7eb',
              paddingBottom: '8px'
            }}>
              Security Analysis
            </h3>
            <div style={{ marginBottom: '16px' }}>
              <p style={{ color: '#4b5563', lineHeight: '1.6' }}>
                {analysis["Security Analysis"].Overview || 'No security overview available'}
              </p>
            </div>
            
            {analysis["Security Analysis"].Vulnerabilities && analysis["Security Analysis"].Vulnerabilities.length > 0 && (
              <div style={{ marginTop: '16px' }}>
                <h4 style={{ 
                  fontSize: '1rem', 
                  marginBottom: '12px', 
                  color: '#dc2626' 
                }}>
                  Vulnerabilities Detected
                </h4>
                <div style={{ 
                  display: 'grid', 
                  gap: '12px' 
                }}>
                  {analysis["Security Analysis"].Vulnerabilities.map((item, index) => (
                    <div key={index} style={{
                      padding: '16px',
                      background: '#fef2f2',
                      borderRadius: '8px',
                      borderLeft: '4px solid #dc2626'
                    }}>
                      <div style={{ 
                        fontWeight: 600, 
                        color: '#dc2626',
                        marginBottom: '4px'
                      }}>
                        {item.Type || 'Unknown Vulnerability'}
                      </div>
                      <div style={{ color: '#4b5563', fontSize: '0.9rem' }}>
                        {item.Description || 'No description available'}
                      </div>
                      {item.Location && (
                        <div style={{ 
                          marginTop: '8px',
                          fontSize: '0.85rem',
                          color: '#6b7280'
                        }}>
                          Location: {item.Location}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
        
        {/* Dependencies Analysis */}
        {analysis["Dependency Analysis"] && (
          <div style={{ marginTop: '32px' }}>
            <h3 style={{ 
              fontSize: '1.2rem', 
              marginBottom: '16px', 
              color: '#3b82f6',
              borderBottom: '2px solid #e5e7eb',
              paddingBottom: '8px'
            }}>
              Dependencies Analysis
            </h3>
            <div style={{ marginBottom: '16px' }}>
              <p style={{ color: '#4b5563', lineHeight: '1.6' }}>
                {analysis["Dependency Analysis"].Overview || 'No dependency overview available'}
              </p>
            </div>
            
            {analysis["Dependency Analysis"].Outdated && analysis["Dependency Analysis"].Outdated.length > 0 && (
              <div style={{ marginTop: '16px' }}>
                <h4 style={{ 
                  fontSize: '1rem', 
                  marginBottom: '12px', 
                  color: '#f59e0b' 
                }}>
                  Outdated Dependencies
                </h4>
                <div style={{ 
                  display: 'grid', 
                  gap: '12px',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))'
                }}>
                  {analysis["Dependency Analysis"].Outdated.map((item, index) => (
                    <div key={index} style={{
                      padding: '16px',
                      background: '#fffbeb',
                      borderRadius: '8px',
                      borderLeft: '4px solid #f59e0b'
                    }}>
                      <div style={{ 
                        fontWeight: 600, 
                        color: '#92400e',
                        marginBottom: '4px'
                      }}>
                        {item.Name || 'Unknown Package'}
                      </div>
                      <div style={{ 
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        fontSize: '0.9rem'
                      }}>
                        <span style={{ color: '#b45309' }}>Current: {item.CurrentVersion || 'n/a'}</span>
                        <svg style={{ width: '12px', height: '12px' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 5l7 7-7 7M5 5l7 7-7 7" />
                        </svg>
                        <span style={{ color: '#059669' }}>Latest: {item.LatestVersion || 'n/a'}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
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