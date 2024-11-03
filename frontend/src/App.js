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
      const res = await axios.post('/query', { query, course_name: courseName });
      setResponse(res.data.response);
    } catch (error) {
      console.error('Error fetching data:', error);
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

        {/* New input for course name */}
        <div className="search-input">
          <input
            type="text"
            value={courseName}
            onChange={(e) => setCourseName(e.target.value)}
            placeholder="Enter course name... (ex. CS 3780, CS 2110, MATH 2940)"
            className="input-field"
          />
        </div>

        {/* Existing input for query */}
        <div className="search-input">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="I want to look for... (ex. Summarize lecture 1 for me)"
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
