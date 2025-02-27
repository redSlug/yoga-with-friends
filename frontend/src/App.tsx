import { useState, useEffect } from 'react';
import './App.css';
import events from './data/events.json';
type Event = {
  time: string;
  meridiem: string;
  day_of_week: string;
  date: string;
};

function App() {
  const [eventData, setEventData] = useState<Array<Event>>([]);

  useEffect(() => {
    setEventData(events);
  }, []);

  return (
    <div className="App">
      <h1>Bradley's Yoga Classes</h1>
      <ul>
        {eventData.map((event, index) => (
          <li key={index}>
            {event.day_of_week}, {event.date} at {event.time}
            {event.meridiem}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;
