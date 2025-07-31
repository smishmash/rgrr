import React, { useState, useEffect } from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import './App.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

function App() {
  const [distributions, setDistributions] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [chartData, setChartData] = useState(null);
  const [maxY, setMaxY] = useState(undefined);

  useEffect(() => {
    fetch('/simulations/dummy/distribution')
      .then(response => response.json())
      .then(data => {
        setDistributions(data);
        if (data.length > 0) {
          const counts = data[0].reduce((acc, value) => {
            acc[value] = (acc[value] || 0) + 1;
            return acc;
          }, {});
          setMaxY(Math.max(...Object.values(counts)) * 1.1);
        }
      });
  }, []);

  useEffect(() => {
    if (distributions.length > 0) {
      const distribution = distributions[currentIndex];
      const counts = distribution.reduce((acc, value) => {
        acc[value] = (acc[value] || 0) + 1;
        return acc;
      }, {});

      const labels = Object.keys(counts);
      const values = Object.values(counts);

      setChartData({
        labels: labels,
        datasets: [
          {
            label: `Resource Distribution ${currentIndex + 1}`,
            data: values,
            backgroundColor: 'rgba(75, 192, 192, 0.6)',
            animation: false,
          },
        ],
      });
    }
  }, [distributions, currentIndex]);

  const handleNext = () => {
    setCurrentIndex((prevIndex) => (prevIndex + 1) % distributions.length);
  };

  const handlePrev = () => {
    setCurrentIndex((prevIndex) => (prevIndex - 1 + distributions.length) % distributions.length);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Simulation Results</h1>
        {chartData ? (
          <div style={{ width: '80%', margin: 'auto' }}>
            <Bar
              key={currentIndex}
              data={chartData}
              options={{
                animation: false,
                scales: {
                  y: {
                    beginAtZero: true,
                    max: maxY,
                  },
                },
              }}
            />
            <div>
              <button onClick={handlePrev} disabled={distributions.length <= 1}>Previous</button>
              <button onClick={handleNext} disabled={distributions.length <= 1}>Next</button>
            </div>
          </div>
        ) : (
          <p>Loading...</p>
        )}
      </header>
    </div>
  );
}

export default App;
