import React, { useState, useEffect, useRef } from 'react';
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
  const [chartInstance, setChartInstance] = useState(null);
  const previousMaxYRef = useRef(undefined);
  const animationFrameId = useRef(null);

  const chartRefCallback = (node) => {
    if (node) {
      setChartInstance(node);
    }
  };

  useEffect(() => {
    fetch('/simulations/dummy/distribution')
      .then(response => response.json())
      .then(data => {
        setDistributions(data);
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

      previousMaxYRef.current = maxY;
      setMaxY(Math.max(...values) * 1.1 || 10);

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

  useEffect(() => {
    if (typeof maxY === 'undefined' || !chartInstance || !chartData) {
      return;
    }

    const chart = chartInstance;
    const startY = previousMaxYRef.current !== undefined ? previousMaxYRef.current : maxY;
    const endY = maxY;
    const duration = 500;
    let startTime = null;

    const animate = (timestamp) => {
      if (!startTime) {
        startTime = timestamp;
      }

      const elapsed = timestamp - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const easedProgress = 1 - Math.pow(1 - progress, 3); // easeOutCubic

      const currentY = startY + (endY - startY) * easedProgress;
      chart.options.scales.y.max = currentY;
      chart.update('none');

      if (progress < 1) {
        animationFrameId.current = requestAnimationFrame(animate);
      }
    };

    cancelAnimationFrame(animationFrameId.current);
    animationFrameId.current = requestAnimationFrame(animate);

    return () => {
      cancelAnimationFrame(animationFrameId.current);
    };
  }, [maxY, chartData, chartInstance]);


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
              ref={chartRefCallback}
              data={chartData}
              options={{
                animation: false,
                scales: {
                  y: {
                    beginAtZero: true,
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
