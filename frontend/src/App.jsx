import React, { useState, useEffect } from "react";
import axios from "axios";
import { Toaster, toast } from "react-hot-toast";

const API_BASE_URL = "http://127.0.0.1:8000/api";

function App() {
  const [status, setStatus] = useState({
    mysql: "Offline",
    postgresql: "Offline",
  });
  const [logs, setLogs] = useState([]);
  const [user, setUser] = useState({ name: "", email: "", password: "" });
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    checkStatus();
    fetchLogs();
  }, []);

  const checkStatus = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/status`);
      setStatus(res.data);
    } catch (e) {
      console.error("Status error");
    }
  };

  const fetchLogs = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/logs`);
      setLogs(res.data);
    } catch (e) {
      console.error("Logs error");
    }
  };

  const filteredLogs = logs.filter(
    (log) =>
      log.id.toString().includes(searchTerm) ||
      log.status.toLowerCase().includes(searchTerm.toLowerCase()),
  );

  return (
    <div className="min-h-screen bg-[#070b14] text-slate-300 p-8 selection:bg-teal-500/20">
      <Toaster position="top-right" />

      {/* Header Updated with Company Name */}
      <header className="max-w-7xl mx-auto flex justify-between items-center mb-12">
        <div>
          <h1 className="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-teal-400 to-blue-500 tracking-tight">
            ERA BIZ SOLUTIONS
          </h1>
          <p className="text-[10px] uppercase tracking-[0.3em] text-slate-500 mt-1">
            Infrastructure Control Center
          </p>
        </div>
        <div className="flex gap-2">
          {["MySQL", "Postgres"].map((db) => (
            <div
              key={db}
              className="px-4 py-2 border border-slate-800 rounded-lg bg-[#0d121d] flex items-center gap-3"
            >
              <span
                className={`w-2 h-2 rounded-full ${status[db.toLowerCase()] === "Connected" ? "bg-teal-500 shadow-[0_0_8px_teal]" : "bg-red-500"}`}
              ></span>
              <span className="text-[11px] font-bold text-slate-400 uppercase">
                {db}
              </span>
            </div>
          ))}
        </div>
      </header>

      <main className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Control Panel */}
        <div className="lg:col-span-4 space-y-8">
          <div className="bg-[#0d121d] p-8 rounded-2xl border border-slate-800 shadow-[0_0_20px_rgba(0,0,0,0.5)]">
            <h3 className="text-sm font-bold text-white mb-6 uppercase tracking-wider flex items-center gap-2">
              <span className="w-1.5 h-1.5 bg-teal-500"></span> Source Injector
            </h3>
            <div className="space-y-4">
              {["name", "email", "password"].map((f) => (
                <input
                  key={f}
                  className="w-full bg-[#070b14] border border-slate-800 p-3 rounded-lg text-sm text-white focus:border-teal-500 outline-none transition-all"
                  placeholder={f.toUpperCase()}
                  onChange={(e) => setUser({ ...user, [f]: e.target.value })}
                />
              ))}
              <button className="w-full bg-gradient-to-r from-teal-600 to-blue-600 hover:from-teal-500 hover:to-blue-500 p-3 rounded-lg text-xs font-bold text-white shadow-lg transition-all transform hover:-translate-y-1">
                EXECUTE_SYNC
              </button>
            </div>
          </div>
        </div>

        {/* Right Dashboard */}
        <div className="lg:col-span-8 space-y-8">
          <div className="bg-gradient-to-br from-[#0d121d] to-[#12192b] p-10 rounded-2xl border border-slate-800 relative overflow-hidden text-center">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-teal-500 to-blue-500"></div>
            <h2 className="text-xl font-bold text-white mb-4">
              Migration Command Core
            </h2>
            <button className="px-8 py-3 border border-slate-700 hover:border-teal-500 hover:text-teal-400 rounded-full text-xs font-bold tracking-widest transition-all">
              INITIALIZE_TRANSFER
            </button>
          </div>

          <div className="bg-[#0d121d] p-8 rounded-2xl border border-slate-800">
            <div className="flex justify-between items-center mb-8">
              <h3 className="text-xs font-bold text-white uppercase tracking-widest">
                Global Log Stream
              </h3>
              <input
                className="bg-[#070b14] border border-slate-800 px-4 py-2 rounded-lg text-[10px] w-40 text-slate-400 focus:border-teal-500 outline-none"
                placeholder="FILTER_LOGS..."
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <div className="max-h-[300px] overflow-y-auto scrollbar-none">
              <table className="w-full text-left text-[11px]">
                <thead className="text-slate-600 border-b border-slate-800 sticky top-0 bg-[#0d121d]">
                  <tr>
                    <th className="pb-4">STREAM_ID</th>
                    <th className="pb-4">STATUS</th>
                    <th className="pb-4">TIMESTAMP</th>
                  </tr>
                </thead>
                <tbody className="text-slate-400">
                  {filteredLogs.map((log) => (
                    <tr
                      key={log.id}
                      className="border-b border-slate-900 hover:bg-[#12192b]"
                    >
                      <td className="py-4 font-mono text-teal-400">{log.id}</td>
                      <td className="py-4">
                        <span
                          className={`px-2 py-1 rounded text-[9px] font-bold ${log.status === "SUCCESS" ? "text-teal-400 bg-teal-500/10" : "text-red-400 bg-red-500/10"}`}
                        >
                          {log.status}
                        </span>
                      </td>
                      <td className="py-4 font-mono">
                        {new Date(log.timestamp).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
