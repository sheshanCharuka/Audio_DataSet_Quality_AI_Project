import React, { useEffect, useState } from "react";
import { Container, Row, Col, Card, Spinner } from "react-bootstrap";
import { Pie, Bar } from "react-chartjs-2";
import "bootstrap/dist/css/bootstrap.min.css";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
} from "chart.js";

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title);

function DatasetDashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://127.0.0.1:5000/stats")
      .then((res) => res.json())
      .then((data) => {
        setStats(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error fetching stats:", err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <Container className="text-center mt-5 text-light" style={{ backgroundColor: "#121212", minHeight: "100vh" }}>
        <Spinner animation="border" variant="light" />
        <p>Loading dataset stats...</p>
      </Container>
    );
  }

  if (!stats) {
    return (
      <Container className="text-center mt-5 text-light" style={{ backgroundColor: "#121212", minHeight: "100vh" }}>
        <h3>Failed to load stats.</h3>
      </Container>
    );
  }

  // --- Pie chart for clean vs quarantined ---
  const pieData = {
    labels: ["Clean", "Quarantined"],
    datasets: [
      {
        data: [stats.clean_files, stats.quarantined_files],
        backgroundColor: ["#28a745", "#dc3545"],
        hoverOffset: 10,
      },
    ],
  };

  // --- Bar chart for top failure reasons ---
  const barData = {
    labels: stats.top_failure_reasons.map((item) => item[0]),
    datasets: [
      {
        label: "Failure Count",
        data: stats.top_failure_reasons.map((item) => item[1]),
        backgroundColor: "#ffc107",
      },
    ],
  };

  const cardStyle = { backgroundColor: "#1e1e1e", color: "#f1f1f1", border: "none" };
  const pageStyle = { backgroundColor: "#121212", minHeight: "100vh", paddingBottom: "50px" };

  return (
    <div style={pageStyle}>
      <Container className="mt-4">
        <h1 className="text-center mb-4 text-light">Audio Dataset Dashboard</h1>

        {/* Summary Cards */}
        <Row className="mb-4">
          <Col md={3} sm={6} className="mb-3">
            <Card className="text-center shadow-sm" style={cardStyle}>
              <Card.Body>
                <Card.Title>Raw Files</Card.Title>
                <Card.Text>{stats.raw_files}</Card.Text>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3} sm={6} className="mb-3">
            <Card className="text-center shadow-sm" style={cardStyle}>
              <Card.Body>
                <Card.Title>Clean Files</Card.Title>
                <Card.Text>{stats.clean_files} ({stats.clean_pct}%)</Card.Text>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3} sm={6} className="mb-3">
            <Card className="text-center shadow-sm" style={cardStyle}>
              <Card.Body>
                <Card.Title>Quarantined Files</Card.Title>
                <Card.Text>{stats.quarantined_files} ({stats.quarantine_pct}%)</Card.Text>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3} sm={6} className="mb-3">
            <Card className="text-center shadow-sm" style={cardStyle}>
              <Card.Body>
                <Card.Title>Augmented Files</Card.Title>
                <Card.Text>{stats.augmented_files}</Card.Text>
              </Card.Body>
            </Card>
          </Col>
        </Row>

        {/* Charts */}
        <Row>
          <Col md={6} className="mb-4">
            <Card className="shadow-sm" style={cardStyle}>
              <Card.Body>
                <Card.Title className="text-center">Clean vs Quarantined</Card.Title>
                <Pie 
                  data={pieData} 
                  options={{
                    plugins: {
                      legend: { labels: { color: "#f1f1f1" } },
                      title: { display: true, color: "#f1f1f1", text: "Clean vs Quarantined Distribution" },
                    },
                  }}
                />
              </Card.Body>
            </Card>
          </Col>
          <Col md={6} className="mb-4">
            <Card className="shadow-sm" style={cardStyle}>
              <Card.Body>
                <Card.Title className="text-center">Top Failure Reasons</Card.Title>
                <Bar 
                  data={barData} 
                  options={{ 
                    responsive: true, 
                    plugins: { 
                      legend: { display: false },
                      title: { display: true, text: "Top Failure Reasons", color: "#f1f1f1" }
                    },
                    scales: {
                      x: { ticks: { color: "#f1f1f1" } },
                      y: { ticks: { color: "#f1f1f1" } }
                    }
                  }} 
                />
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    </div>
  );
}

export default DatasetDashboard;
