import React, { useState } from 'react';
import axios from 'axios';
import './App.css';


function App() {
  const [query, setQuery] = useState('');
  const [courseName, setCourseName] = useState('');
  const [response, setResponse] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const courses = [
    { value: '', label: 'Select a course...' },
    // { value: 'ARCH 1901', label: 'ARCH 1901 FWS: Topics in Architecture ' },
    // { value: 'ARTH 1100', label: 'ARTH 1100 Art Histories: An Introduction' },
    { value: 'ASIAN 1111 FWS: Literature, Culture, Religion (2023FA) ', label: 'ASIAN 1111 FWS: Literature, Culture, Religion ' },
    { value: 'CS 3780 COMBINED-COMEET Introduction to Machine Learning (2024FA)', label: 'CS 3780 Introduction to Machine Learning ' },
    { value: 'ENGRD 2700 Basic Engineering Probability and Statistics (2024SP)', label: 'ENGRD 2700 Basic Engineering Probability and Statistics ' },
    { value: 'ENGRG 1050 Engineering Seminar (2023FA)', label: 'ENGRG 1050 Engineering Seminar ' },
    // { value: 'ENGRG 1400', label: 'ENGRG 1400 Engineering Project Team Onboarding ' },
    // { value: 'ENGRI 1270', label: 'ENGRI 1270 Introduction to Entrepreneurship for Engineers ' },
    // { value: 'Introduction to Analysis of Algorithms', label: 'CS 4820 Introduction to Analysis of Algorithms ' },
    // { value: 'MATH 2930', label: 'MATH 2930 Differential Equations for Engineers ' },
    // { value: 'MATH 2940', label: 'MATH 2940 Linear Algebra for Engineers ' },
    // { value: 'ORIE 3500', label: 'ORIE 3500 Eng Probability and Statistics: Modeling and Data Science II ' },
    { value: 'PHYS 1110 Introduction to Experimental Physics (2023FA)', label: 'PHYS 1110 Introduction to Experimental Physics ' }
  ];


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
        {/* Dropdown for selecting course */}
        <div className="search-input">
          <select
            value={courseName}
            onChange={(e) => setCourseName(e.target.value)}
            className="input-field"
          >
            {courses.map((course) => (
              <option key={course.value} value={course.value}>
                {course.label}
              </option>
            ))}
          </select>
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
