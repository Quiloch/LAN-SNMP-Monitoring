import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts';

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

  // --- Funkcje pomocnicze ---
  
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

  // --- Główna logika danych ---

  // Funkcja sprawdzająca alerty (wyciągnięta, aby była dostępna w useEffect)
  const checkAlerts = (data) => {
      const newAlerts = [];
      const cpu = parseFloat(data.cpuUsage);
      
      // Alert: Wysokie CPU
      if (cpu > 80) {
          newAlerts.push({
              id: 1, 
              type: 'critical', 
              msg: `KRYTYCZNE: Obciążenie CPU wynosi ${cpu}% (Próg: 80%)`
          });
      }
      
      // Alert: Awaria interfejsu
      if (data.if2_Status === '2') {
           newAlerts.push({
              id: 2, 
              type: 'warning', 
              msg: `OSTRZEŻENIE: Interfejs GigabitEthernet0/1 jest DOWN`
          });
      }

      // Alert: Błędy
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
      // setDebugInfo(`Pobieranie z ${API_URL}...`);
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
      {/* STYLE CSS WBUDOWANE BEZPOŚREDNIO 
          To gwarantuje, że style się załadują niezależnie od konfiguracji buildera
      */}
      <style>{`
        body { background-color: #f0f2f5; margin: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .App { padding: 20px; text-align: center; padding-bottom: 80px; }
        
        /* Header */
        .App-header { 
            background-color: #2c3e50; 
            padding: 20px; 
            color: white; 
            border-radius: 8px; 
            margin-bottom: 20px; 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
        }
        .header-content h1 { font-size: 1.5rem; margin: 0; }
        
        /* Grid */
        .dashboard-grid { display: grid; grid-template-columns: 1fr; gap: 20px; max-width: 1200px; margin: 0 auto; }
        @media (min-width: 768px) { .dashboard-grid { grid-template-columns: repeat(2, 1fr); } .full-width { grid-column: span 2; } }
        
        /* Karty */
        .card { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); text-align: left; }
        .card h2 { margin-top: 0; color: #34495e; border-bottom: 1px solid #eee; padding-bottom: 10px; margin-bottom: 15px; font-size: 1.2rem; }
        
        /* Tabela */
        .interface-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
        .interface-table th, .interface-table td { padding: 12px; border-bottom: 1px solid #eee; }
        .interface-table th { text-align: left; background-color: #f8f9fa; color: #7f8c8d; }
        
        /* Statystyki */
        .stat-value { font-size: 2.5rem; font-weight: bold; text-align: center; margin-top: 10px; color: #2c3e50; }
        
        /* Status Badges */
        .status-badge { padding: 5px 10px; border-radius: 4px; font-weight: bold; }
        .status-online { background: #d5f5e3; color: #27ae60; }
        .status-offline { background: #fadbd8; color: #c0392b; }
        
        /* Alerty */
        .alerts-container { max-width: 1200px; margin: 0 auto 20px auto; }
        .alert-box { 
            padding: 15px; margin-bottom: 10px; border-radius: 8px; text-align: left; font-weight: bold; border-left: 5px solid; 
            animation: pulse 2s infinite; 
        }
        .alert-critical { background-color: #fadbd8; color: #c0392b; border-color: #e74c3c; }
        .alert-warning { background-color: #fcf3cf; color: #9a7d0a; border-color: #f1c40f; }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.8; } 100% { opacity: 1; } }
        
        /* Przycisk */
        .btn-report { 
            background-color: #3498db; color: white; border: none; padding: 10px 20px; 
            border-radius: 5px; cursor: pointer; font-size: 1rem; transition: background 0.3s; font-weight: bold; 
        }
        .btn-report:hover { background-color: #2980b9; }

        /* Debugger */
        .btn-debug-toggle { position: fixed; bottom: 20px; right: 20px; background: #333; color: #fff; border: none; width: 40px; height: 40px; border-radius: 50%; cursor: pointer; opacity: 0.5; transition: opacity 0.3s; font-size: 1.2rem; z-index: 9999; }
        .btn-debug-toggle:hover { opacity: 1; }
        .debug-box { background: #222; color: #0f0; padding: 15px; font-family: monospace; overflow-x: auto; border-radius: 5px; margin-top: 40px; text-align: left; border: 1px solid #444; max-width: 1200px; margin-left: auto; margin-right: auto; }
        
        .info-detail { margin-bottom: 8px; font-size: 0.95rem; }
        .info-label { font-weight: 600; color: #555; width: 100px; display: inline-block; }
      `}</style>

      <header className="App-header">
        <div className="header-content">
            <h1 style={{margin: 0}}>📡 SNMP Monitoring</h1>
            <small>Panel Administratora Sieci</small>
        </div>
        <button className="btn-report" onClick={handleDownloadReport}>
            📄 Raport PDF
        </button>
      </header>
      
      {/* KONTENER ALERTÓW */}
      <div className="alerts-container">
          {error && <div className="alert-box alert-critical">⚠️ {error}</div>}
          
          {alerts.map(alert => (
              <div key={alert.id} className={`alert-box alert-${alert.type}`}>
                  🚨 {alert.msg}
              </div>
          ))}
      </div>

      <div className="dashboard-grid">
        {/* Karta Statusu */}
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
            {/* Wartość CPU - Czerwona jeśli > 80 */}
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

        {/* Tabela Interfejsów */}
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

      {/* Przycisk Debuggera (Dół, Prawa strona) */}
      <button className="btn-debug-toggle" onClick={() => setShowDebug(!showDebug)} title="Pokaż/Ukryj konsolę diagnostyczną">
        🛠️
      </button>

    </div>
  );
}

export default App;