import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');

  const handleSearch = async () => {
    const res = await axios.post('/query', { query, course_id: '12345' });
    setResponse(res.data.response);
  };

  return (
    <div>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search course materials"
      />
      <button onClick={handleSearch}>Search</button>
      <div>{response}</div>
    </div>
  );
}

export default App;
