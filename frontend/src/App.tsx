import './App.css';
import events from './assets/yoga.json';

type Event = {
  instructor: string;
  location: string;
  timestamp: number;
  time: string;
  meridiem: string;
  day_of_week: string;
  date: string;
};


function App() {
  return (
    <div className="App">
      <h1>Enrolled Yoga Classes</h1>
      <ul>
        {events.map((event: Event, index: number) => (
          <li key={index}>
              {event.time}{event.meridiem} {event.date} - {event.instructor.split(" ")[0]} - {event.location}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;
