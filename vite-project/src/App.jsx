import { useState, useEffect } from 'react'
import './App.css'
import { PieChart } from '@mui/x-charts/PieChart';
import { List, ListItem } from '@mui/material';
import { LineChart } from '@mui/x-charts/LineChart';

function App() {
  const [sentiment, setSentiment] = useState([]);
  const [message, setMessage] = useState([]);
  const [analysis_by_time, setCheckTime] = useState([]);
  function formatData(data) {
    return [
      { id: 0, value: data.total_positive ?? 0, label: 'Positive' },
      { id: 1, value: data.total_negative ?? 0, label: 'Negative' },
      { id: 2, value: data.total_neutral ?? 0, label: 'Neutral' },
    ];
  }
  function normalizeData(dataArray) {
    return dataArray.map(data => {
      const hourDate = new Date(data.check_time);
      const total = data.total_messages;
      return {
        Hour: hourDate,
        positive: total ? Number((data.total_positive_count / total * 100).toFixed(2)) : 0,
        negative: total ? Number((data.total_negative_count / total * 100).toFixed(2)) : 0,
        neutral: total ? Number((data.total_neutral_count / total * 100).toFixed(2)) : 0,
      };
    });
  }
  useEffect(() => {
    const fetchData = () => {
      fetch('http://localhost:8000/stats/sentiment/summary')
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(data => {
          setSentiment(formatData(data));
        })
        .catch(error => {
          console.error('Error fetching data:', error);
        });

      fetch('http://localhost:8000/messages/sentiment')
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(data => {
          setMessage(data.messages);
        })
        .catch(error => {
          console.error('Error fetching data:', error);
        });

      fetch('http://localhost:8000/stats/sentiment/iter')
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(data => {
          const normalizedData = normalizeData(data);
          setCheckTime(normalizedData);
        })
        .catch(error => {
          console.error('Error fetching data:', error);
        });
    };

    // Fetch data immediately and then set interval
    fetchData();
    const intervalId = setInterval(fetchData, 1000);

    // Cleanup interval on component unmount
    return () => clearInterval(intervalId);
  }, []);
    return (
    <div className="container">
      <div style={{ flex: 7 }}>
        <PieChart 
          series={[
            {
              data: sentiment,
            },
          ]}
          width={600}
          height={400}
        />
    <LineChart
      height={400}
      series={[
        {
          data: analysis_by_time.map(item => item.positive),
          label: 'Positive',
          area: true,
          stack: 'total',
          showMark: false,
        },
        {
          data: analysis_by_time.map(item => item.negative),
          label: 'Negative',
          area: true,
          stack: 'total',
          showMark: false,
        },
        {
          data: analysis_by_time.map(item => item.neutral),
          label: 'Neutral',
          area: true,
          stack: 'total',
          showMark: false,
        }
      ]}
      xAxis={[{
        data: analysis_by_time.map(item => item.Hour),
        scaleType: 'time',
        valueFormatter: (item) => item.getSeconds().toString(),
      }]}

    />
      </div>
      <div style={{ flex: 3 }}>
      <List>
          {message.map(item => (
          <ListItem key={item.id}>
              {item.latest_post_time}
              <br />
              {item.message_content} 
              <br />
              @{item.thread_url}
          </ListItem>
        ))}
      </List>
      </div>
    </div>
  )
}

export default App
