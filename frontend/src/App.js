import React, { useState } from 'react';
import axios from 'axios';
import './App.css';


function App() {
  const [query, setQuery] = useState('');
  const [courseName, setCourseName] = useState('');
  const [response, setResponse] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSearch = async () => {
    setIsLoading(true);
    try {
      console.log("Query:", query); // Debug log
      console.log("Course Name:", courseName); // Debug log

      const url = `https://xfpjovpqg4.execute-api.us-east-1.amazonaws.com/dev/Search?course=${encodeURIComponent(courseName)}&query=${encodeURIComponent(query)}`;
      console.log("Request URL:", url); // Debug log

      const res = await axios.get(url);
      console.log("Full Response:", res); // Debug log

      // Directly set the response's body
      setResponse(res.data || "No response found");

    } catch (error) {
      if (error.response) {
        // Server responded with a status other than 2xx
        console.error('Response Error:', error.response);
        setResponse(`Server Error: ${error.response.status} - ${error.response.data || 'Unknown error'}`);
      } else if (error.request) {
        // Request was made, but no response received
        console.error('No Response:', error.request);
        setResponse('No response received. Please check your network.');
      } else {
        // Other errors (e.g., incorrect request setup)
        console.error('Error:', error.message);
        setResponse(`Error: ${error.message}`);
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      <div className="search-card">
        <h1 className="card-title">MyCourseIndex v2</h1>
        <p className="card-description">Search course materials from Ed and Canvas</p>

        {/* Input for course name */}
        <div className="search-input">
          <input
            type="text"
            value={courseName}
            onChange={(e) => setCourseName(e.target.value)}
            placeholder="Enter course name... (e.g., CS 3780, CS 2110, MATH 2940)"
            className="input-field"
          />
        </div>

        {/* Input for query */}
        <div className="search-input">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="I want to look for... (e.g., Summarize lecture 1 for me)"
            className="input-field"
          />
          <button onClick={handleSearch} disabled={isLoading} className="search-button">
            {isLoading ? 'Searching...' : 'Search'}
          </button>
        </div>

        {response && (
          <div className="response-card">
            <p>{response}</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
