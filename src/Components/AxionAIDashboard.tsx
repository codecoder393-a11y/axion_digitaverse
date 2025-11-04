import { useEffect, useState } from "react";

function AxionAIDashboard() {
  const [report, setReport] = useState<any>(null);

  useEffect(() => {
    fetch("http://127.0.0.1:5001/api/axion-ai/dashboard")
      .then(res => res.json())
      .then(setReport);
  }, []);

  if (!report) return <div>Loading AI dashboard...</div>;

  return (
    <div className="container py-4">
      <h2 className="fw-bold mb-3">Axion AI Blockchain Dashboard</h2>
      <div className="mb-3">
        <h5>Stats</h5>
        <ul>
          {Object.entries(report.stats).map(([k, v]) => (
            <li key={k}>
              <b>{k}:</b> {String(v)}
            </li>
          ))}
        </ul>
      </div>
      <div className="mb-3">
        <h5>Anomalies</h5>
        {report.anomalies.length === 0 ? (
          <span>No anomalies detected.</span>
        ) : (
          <ul>
            {report.anomalies.map((a: any, i: number) => (
              <li key={i}>{a}</li>
            ))}
          </ul>
        )}
      </div>
      <div className="mb-3">
        <h5>Optimization</h5>
        <div>{report.optimization}</div>
      </div>
    </div>
  );
}

export default AxionAIDashboard;