import './App.css';
import {useEffect, useState} from "react";

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
    const [yogaData, setYogaData] = useState<Array<Event>>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            const response = await fetch(import.meta.env.VITE_YOGA_DATA_URL!);
            setYogaData(await response.json());
            setLoading(false);
        };
        fetchData();
    }, []);

    if (loading) {
        return <p>Loading...</p>;
    }

    return (
    <div className="App">
      <h1>Enrolled Yoga Classes</h1>
        {yogaData.length === 0 ? (<p>Sign up for some classes!</p>) :
            (<ul>
                {yogaData.map((event: Event, index: number) => (
                    <li key={index}>
                        {event.time}{event.meridiem} {event.date} - {event.instructor.split(" ")[0]} - {event.location}
                    </li>
                ))}
            </ul>)
        }
    </div>
    );
}

export default App;
