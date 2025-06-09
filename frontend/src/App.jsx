import { useState } from 'react';

function App() {
  const [projectId, setProjectId] = useState('demo');
  const [jobId, setJobId] = useState('');
  const [error, setError] = useState('');

  const createJob = async () => {
    setError('');
    setJobId('');
    try {
      const res = await fetch('/api/design-jobs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_id: projectId, preview_only: false })
      });
      if (!res.ok) {
        throw new Error('Request failed');
      }
      const data = await res.json();
      setJobId(data.job_id);
    } catch (err) {
      setError('Unable to create job');
    }
  };

  return (
    <div style={{ textAlign: 'center', marginTop: '2rem' }}>
      <h1>YardVision Pro</h1>
      <div style={{ marginTop: '1rem' }}>
        <input
          value={projectId}
          onChange={(e) => setProjectId(e.target.value)}
          placeholder="Project ID"
        />
        <button onClick={createJob} style={{ marginLeft: '0.5rem' }}>
          Create Job
        </button>
      </div>
      {jobId && <p>Job created: {jobId}</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
}

export default App;
