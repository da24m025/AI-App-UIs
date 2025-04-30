import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [features, setFeatures] = useState(Array(30).fill(0));
  const [prediction, setPrediction] = useState(null);
  const [error, setError] = useState(null);

  const handleChange = (index, value) => {
    const newFeatures = [...features];
    newFeatures[index] = parseFloat(value) || 0;
    setFeatures(newFeatures);
  };

  const handlePredict = async () => {
    setError(null);
    setPrediction(null);
    try {
      // call the host‐published backend port
      const response = await axios.post(
        'http://localhost:5001/predict',
        { features }
      );
      setPrediction(response.data.prediction);
    } catch (err) {
      setError(err.response?.data?.error || 'Prediction failed');
    }
  };

  return (
    <div className="container">
      <h1>Fraud Detection Predictor</h1>
      <div className="input-grid">
        {features.map((value, idx) => (
          <div key={idx} className="input-item">
            <label>
              {idx === 0 ? 'Time'
                : idx === 29 ? 'Amount'
                : `V${idx}`}
            </label>
            <input
              type="number"
              value={value}
              onChange={(e) => handleChange(idx, e.target.value)}
              step="any"
            />
          </div>
        ))}
      </div>
      <button onClick={handlePredict}>Predict</button>
      {prediction !== null && (
        <p>Prediction: {prediction === 1 ? 'Fraud' : 'Not Fraud'}</p>
      )}
      {error && <p style={{ color: 'red' }}>Error: {error}</p>}
    </div>
  );
}

export default App;
