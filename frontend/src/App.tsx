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
  waitlisted: boolean;
};


function App() {
    console.log("url is ", import.meta.env.VITE_YOGA_DATA_URL)

    const [yogaData, setYogaData] = useState<Array<Event>>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                const response = await fetch(import.meta.env.VITE_YOGA_DATA_URL!);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                setYogaData(await response.json());
            } catch(e) {
                throw new Error(`Something went wrong while fetching classes. ${e}`);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    if (loading) {
        return <p>Loading...</p>;
    }

    console.log("yogaData is", yogaData)

    const knownLocations = ["Park Slope", "Brooklyn Heights"]

    const parkSlopeClasses = yogaData.filter((e) => e.location === "Park Slope" && !e.waitlisted);
    const brooklynHeights = yogaData.filter((e) => e.location === "Brooklyn Heights" && !e.waitlisted);
    const otherClasses = yogaData.filter((e) => !knownLocations.includes(e.location) && !e.waitlisted);
    const waitlisted = yogaData.filter((e) => e.waitlisted);

    return (
    <div className="App">
        <h1>Yoga Classes</h1>
      <h2>Park Slope (Enrolled)</h2>
        {parkSlopeClasses.length === 0 ? (<p>couldn't find any</p>) :
            (<ul>
                {parkSlopeClasses.map((event: Event, index: number) => (
                    <li key={index}>
                        {event.time}{event.meridiem} {event.date} - {event.instructor.split(" ")[0]}
                    </li>
                ))}
            </ul>)
        }
        <h2>Brooklyn Heights (Enrolled)</h2>
        {brooklynHeights.length === 0 ? (<p>couldn't find any</p>) :
            (<ul>
                {brooklynHeights.map((event: Event, index: number) => (
                    <li key={index}>
                        {event.time}{event.meridiem} {event.date} - {event.instructor.split(" ")[0]}
                    </li>
                ))}
            </ul>)
        }
        <h2>Waitlisted</h2>
        {waitlisted.length === 0 ? (<p>couldn't find any</p>) :
            (<ul>
                {waitlisted.map((event: Event, index: number) => (
                    <li key={index}>
                        {event.time}{event.meridiem} {event.date} - {event.instructor.split(" ")[0]}
                    </li>
                ))}
            </ul>)
        }

        <h2>Other Classes</h2>
        {otherClasses.length === 0 ? (<p>couldn't find any</p>) :
            (<ul>
                {otherClasses.map((event: Event, index: number) => (
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
