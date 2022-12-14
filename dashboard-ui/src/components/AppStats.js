import React, { useEffect, useState } from 'react'
import '../App.css';

export default function AppStats() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null)

	    const getStats = () => {
            
        fetch(`http://lab6-service.canadacentral.cloudapp.azure.com:8100/book/get_stats`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Received Stats")
                setStats(result);
                setIsLoaded(true);
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })
    }
    useEffect(() => {
		const interval = setInterval(() => getStats(), 2000); // Update every 2 seconds
		return() => clearInterval(interval);
    }, [getStats]);

    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
        return(
            <div>
                <h1>Latest Stats</h1>
                <table className={"StatsTable"}>
					<tbody>
						<tr>
							<th>Make Reservation</th>
							<th>Payments</th>
						</tr>
						<tr>
							<td># NumB: {stats['num_book']}</td>
							<td># NumP: {stats['num_payment']}</td>
						</tr>
						<tr>
							<td colspan="2">Sum Book: {stats['sum_book_total']}</td>
						</tr>
						<tr>
							<td colspan="2">Avg Book: {stats['avg_book_total']}</td>
						</tr>
						{/* <tr>
							<td colspan="2">Max HR: {stats['max_bp_sys_reading']}</td>
						</tr> */}
					</tbody>
                </table>
                <h3>Last Updated: {stats['last_updated']}</h3>

            </div>
        )
    }
}
