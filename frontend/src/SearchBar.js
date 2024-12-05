import React, { useState } from 'react';
import axios from 'axios';

function SearchBar() {
  const [courseId, setCourseId] = useState('course-101'); // Default for testing
  const [query, setQuery] = useState('');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);

  const handleQuery = async () => {
    if (!courseId || !query) {
      alert('Please enter a course ID and your question.');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post('https://your-api-id.execute-api.region.amazonaws.com/prod/query', {
        course_id: courseId,
        query: query
      });
      setAnswer(response.data.answer);
    } catch (error) {
      console.error('Error fetching the answer:', error);
      setAnswer('An error occurred while fetching the answer.');
    }
    setLoading(false);
  };

  return (
    <div>
      <h2>Ask a Question</h2>
      <input
        type="text"
        placeholder="Course ID"
        value={courseId}
        onChange={(e) => setCourseId(e.target.value)}
      />
      <input
        type="text"
        placeholder="Your Question"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      <button onClick={handleQuery} disabled={loading}>
        {loading ? 'Processing...' : 'Submit'}
      </button>
      {answer && (
        <div>
          <h3>Answer:</h3>
          <p>{answer}</p>
        </div>
      )}
    </div>
  );
}

export default SearchBar;
