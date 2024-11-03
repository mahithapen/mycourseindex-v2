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
      const url = `https://xfpjovpqg4.execute-api.us-east-1.amazonaws.com/dev/Search?query=${encodeURIComponent(query)}&course_name=${encodeURIComponent(courseName)}`;
      const res = await axios.get(url);

      // Parse the nested JSON response structure
      const parsedBody = JSON.parse(res.data.body);  // Parse the outer body field

      // Set the response with the "generation" field from the parsed JSON
      setResponse(parsedBody.generation || 'No response found');  // Access the "generation" field
    } catch (error) {
      console.error('Error fetching data:', error);  // Log the full error object
      setResponse('An error occurred while searching. Please try again.');
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
