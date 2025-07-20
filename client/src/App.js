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
  const [chartData, setChartData] = useState(null);

  useEffect(() => {
    fetch('/simulations/dummy/distribution')
      .then(response => response.json())
      .then(data => {
        const lastDistribution = data[data.length - 1];
        const counts = lastDistribution.reduce((acc, value) => {
          acc[value] = (acc[value] || 0) + 1;
          return acc;
        }, {});

        const labels = Object.keys(counts);
        const values = Object.values(counts);

        setChartData({
          labels: labels,
          datasets: [
            {
              label: 'Resource Distribution',
              data: values,
              backgroundColor: 'rgba(75, 192, 192, 0.6)',
            },
          ],
        });
      });
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>Simulation Results</h1>
        {chartData ? (
          <Bar data={chartData} />
        ) : (
          <p>Loading...</p>
        )}
      </header>
    </div>
  );
}

export default App;
