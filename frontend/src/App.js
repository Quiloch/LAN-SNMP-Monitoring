import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts';
import './App.css';

const API_URL = 'http://127.0.0.1:5001';

function App() {
  const [currentData, setCurrentData] = useState(null);
  const [historyData, setHistoryData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [alerts, setAlerts] = useState([]);
  
  // Stan do ukrywania/pokazywania debuggera (Przywrócony)
  const [showDebug, setShowDebug] = useState(false);
  const [debugInfo, setDebugInfo] = useState("Inicjalizacja...");
  
  const intervalRef = useRef(null);

  // Funkcje pomocnicze 
  
  const formatBytes = (bytes, decimals = 2) => {
      if (!+bytes) return '0 B';
      const k = 1024;
      const dm = decimals < 0 ? 0 : decimals;
      const sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
  };

  const formatUptime = (ticks) => {
      if (!ticks) return 'N/A';
      const seconds = parseInt(ticks, 10) / 100;
      const days = Math.floor(seconds / (3600 * 24));
      const hours = Math.floor((seconds % (3600 * 24)) / 3600);
      const minutes = Math.floor((seconds % 3600) / 60);
      return `${days}d ${hours}h ${minutes}m`;
  };

  const handleDownloadReport = () => {
      const link = document.createElement('a');
      link.href = `${API_URL}/export/report/pdf`;
      link.setAttribute('download', 'raport.pdf');
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
  };

  // Główna logika danych 

  // Funkcja sprawdzająca alerty (wyciągnięta, aby była dostępna w useEffect)
  const checkAlerts = (data) => {
      const newAlerts = [];
      const cpu = parseFloat(data.cpuUsage);
      
      // Alert dla wysokiego CPU
      if (cpu > 80) {
          newAlerts.push({
              id: 1, 
              type: 'critical', 
              msg: `KRYTYCZNE: Obciążenie CPU wynosi ${cpu}% (Próg: 80%)`
          });
      }
      
      // Alert dla awarii interfejsu
      if (data.if2_Status === '2') {
           newAlerts.push({
              id: 2, 
              type: 'warning', 
              msg: `OSTRZEŻENIE: Interfejs GigabitEthernet0/1 jest DOWN`
          });
      }

      // Alert błędów
      if (parseInt(data.if1_ErrIn, 10) > 0 || parseInt(data.if1_ErrOut, 10) > 0) {
          newAlerts.push({
              id: 3, 
              type: 'warning', 
              msg: `Wykryto błędy transmisji na GigabitEthernet0/0`
          });
      }

      setAlerts(newAlerts);
  };

  const fetchData = async () => {
    try {
      const currentRes = await axios.get(`${API_URL}/snmp`);
      
      setDebugInfo(`Otrzymano dane: ${JSON.stringify(currentRes.data).substring(0, 50)}...`);

      if (currentRes.data && typeof currentRes.data === 'object') {
        setCurrentData(currentRes.data);
        checkAlerts(currentRes.data);
        setError(null);
      }
    } catch (err) {
      console.error("Błąd:", err);
      const msg = err.message;
      setError(`Błąd połączenia: ${msg}`);
      setDebugInfo(`BŁĄD: ${msg}`);
    } finally {
      setLoading(false);
    }
  };

  // Uruchomienie interwału
  useEffect(() => {
    fetchData();
    intervalRef.current = setInterval(fetchData, 5000);
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, []);

  // Aktualizacja historii wykresów
  useEffect(() => {
    if (currentData && !error) {
        const now = new Date().toLocaleTimeString();
        const cpuVal = parseFloat(currentData.cpuUsage);
        const ramVal = parseFloat(currentData.ramUsage);

        if (!isNaN(cpuVal)) {
            setHistoryData(prev => {
                const newPoint = { time: now, cpu: cpuVal, ram: ramVal };
                const newHistory = [...prev, newPoint];
                if (newHistory.length > 20) newHistory.shift();
                return newHistory;
            });
        }
    }
  }, [currentData, error]);

  if (loading && !currentData) return <div style={{padding: 20}}>Ładowanie systemu...</div>;

  return (
    <div className="App">   
      <header className="App-header">
        <div className="header-content">
            <h1 style={{margin: 0}}>📡 SNMP Monitoring</h1>
            <small>Panel Administratora Sieci</small>
        </div>
        <button className="btn-report" onClick={handleDownloadReport}>
            📄 Raport PDF
        </button>
      </header>
      
      {/* Alerty */}
      <div className="alerts-container">
          {error && <div className="alert-box alert-critical">⚠️ {error}</div>}
          
          {alerts.map(alert => (
              <div key={alert.id} className={`alert-box alert-${alert.type}`}>
                  🚨 {alert.msg}
              </div>
          ))}
      </div>

      <div className="dashboard-grid">
        {/* Karta statusu urządzenia*/}
        <div className="card full-width">
            <h2>ℹ️ Status Urządzenia</h2>
            <div style={{display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap'}}>
                <div>
                    <div className="info-detail"><span className="info-label">Urządzenie:</span> {currentData?.sysName || 'Ładowanie...'}</div>
                    <div className="info-detail"><span className="info-label">Opis:</span> {currentData?.sysDescr || '...'}</div>
                    <div className="info-detail"><span className="info-label">Lokalizacja:</span> {currentData?.sysLocation || 'Brak danych'}</div>
                    <div className="info-detail"><span className="info-label">Kontakt:</span> {currentData?.sysContact || 'Brak danych'}</div>
                </div>
                <div style={{textAlign: 'right', minWidth: '150px'}}>
                     <div style={{marginBottom: 10, fontSize: '1.1rem'}}>
                        <strong>Uptime:</strong><br/> 
                        {formatUptime(currentData?.sysUpTime)}
                     </div>
                     <span className={`status-badge ${!currentData?.error ? 'status-online' : 'status-offline'}`}>
                        {!currentData?.error ? 'ONLINE' : 'OFFLINE'}
                    </span>
                </div>
            </div>
        </div>

        {/* Wykres CPU */}
        <div className="card">
            <h3>📈 Obciążenie CPU</h3>
            <div style={{ width: '100%', height: 300 }}>
                 <ResponsiveContainer>
                    <LineChart data={historyData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="time" />
                        <YAxis domain={[0, 100]} unit="%" />
                        <Tooltip />
                        <Line type="linear" dataKey="cpu" stroke="#e74c3c" strokeWidth={3} dot={false} isAnimationActive={false} />
                        <ReferenceLine y={80} stroke="red" strokeDasharray="3 3" />
                    </LineChart>
                </ResponsiveContainer>
            </div>
            {/* Wartość CPU - czerwony jeśli > 80 */}
            <div className="stat-value" style={{color: parseFloat(currentData?.cpuUsage) > 80 ? '#c0392b' : '#2c3e50'}}>
                {currentData?.cpuUsage}%
            </div>
        </div>

        {/* Wykres RAM */}
        <div className="card">
            <h3>📊 Zużycie RAM</h3>
            <div style={{ width: '100%', height: 300 }}>
                 <ResponsiveContainer>
                    <LineChart data={historyData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="time" />
                        <YAxis tickFormatter={(value) => formatBytes(value, 0)} />
                        <Tooltip formatter={(value) => [formatBytes(value), 'RAM']} />
                        <Legend />
                        <Line type="linear" dataKey="ram" stroke="#3498db" strokeWidth={3} dot={false} isAnimationActive={false} />
                    </LineChart>
                </ResponsiveContainer>
            </div>
            <div className="stat-value">
                {formatBytes(currentData?.ramUsage)}
            </div>
        </div>

        {/* Tabela interfejsów */}
        <div className="card full-width">
            <h3>🔌 Status Interfejsów</h3>
            <table className="interface-table">
                <thead>
                    <tr>
                        <th>Interfejs</th>
                        <th>Status</th>
                        <th>Ruch IN</th>
                        <th>Ruch OUT</th>
                        <th>Błędy (In/Out)</th>
                    </tr>
                </thead>
                <tbody>
                    {[1, 2].map(id => (
                        <tr key={id}>
                            <td>{currentData?.[`if${id}_Name`] || `Fa0/${id-1}`}</td>
                            <td>
                                <span style={{
                                    color: currentData?.[`if${id}_Status`] === '1' ? '#27ae60' : '#c0392b',
                                    fontWeight: 'bold'
                                }}>
                                    {currentData?.[`if${id}_Status`] === '1' ? '● UP' : '● DOWN'}
                                </span>
                            </td>
                            <td>{formatBytes(currentData?.[`if${id}_In`] || 0)}</td>
                            <td>{formatBytes(currentData?.[`if${id}_Out`] || 0)}</td>
                            
                            <td style={{
                                color: (parseInt(currentData?.[`if${id}_ErrIn`], 10) > 0 || parseInt(currentData?.[`if${id}_ErrOut`], 10) > 0) ? '#c0392b' : '#7f8c8d',
                                fontWeight: (parseInt(currentData?.[`if${id}_ErrIn`], 10) > 0 || parseInt(currentData?.[`if${id}_ErrOut`], 10) > 0) ? 'bold' : 'normal'
                            }}>
                                {currentData?.[`if${id}_ErrIn`] || 0} / {currentData?.[`if${id}_ErrOut`] || 0}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
      </div>

      {showDebug && (
        <div className="debug-box">
            <h3>🛠️ Diagnostyka Systemu</h3>
            <p><strong>API URL:</strong> {API_URL}</p>
            <p><strong>Ostatni status:</strong> {error ? error : "OK"}</p>
            <p><strong>Log zdarzeń:</strong> {debugInfo}</p>
            <hr style={{borderColor: '#444'}}/>
            <p>Punkty danych: <strong>{historyData.length}</strong></p>
            <p>Surowe dane: {JSON.stringify(currentData)}</p>
        </div>
      )}

      {/* Przycisk Debuggera (Dół z prawej strony) */}
      <button className="btn-debug-toggle" onClick={() => setShowDebug(!showDebug)} title="Pokaż/Ukryj konsolę diagnostyczną">
        🛠️
      </button>

    </div>
  );
}

export default App;