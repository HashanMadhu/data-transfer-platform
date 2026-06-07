import React, { useState, useEffect } from "react";
import axios from "axios";
import { Toaster } from "react-hot-toast";

const API_BASE_URL = "http://127.0.0.1:8000/api";

function App() {
  const [logs, setLogs] = useState([]);
  const [user, setUser] = useState({ name: "", email: "", password: "" });
  const [searchTerm, setSearchTerm] = useState("");

  // පණිවිඩ සඳහා වෙන වෙනම State
  const [userMsg, setUserMsg] = useState({ type: "", text: "" });
  const [migMsg, setMigMsg] = useState({ type: "", text: "" });

  useEffect(() => {
    fetchLogs();
  }, []);

  const fetchLogs = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/logs`);
      setLogs(res.data);
    } catch (e) {
      console.error("Logs error");
    }
  };

  const handleSaveUser = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_BASE_URL}/users/mysql`, user);
      setUserMsg({ type: "success", text: "User saved successfully!" });
      setMigMsg({ type: "", text: "" });
      setUser({ name: "", email: "", password: "" });
    } catch (err) {
      setUserMsg({ type: "error", text: "Failed to save user." });
    }
  };

  const triggerMigration = async () => {
    try {
      await axios.post(`${API_BASE_URL}/migrate`);
      setMigMsg({ type: "success", text: "Migration started successfully!" });
      setUserMsg({ type: "", text: "" });
      fetchLogs();
    } catch (err) {
      setMigMsg({ type: "error", text: "Migration failed." });
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

      <header className="max-w-7xl mx-auto mb-12">
        <h1 className="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-teal-400 to-blue-500">
          ERA BIZ SOLUTIONS
        </h1>
        <p className="text-[10px] uppercase tracking-[0.3em] text-slate-500 mt-1">
          Infrastructure Control Center
        </p>
      </header>

      <main className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Control Panel */}
        <div className="lg:col-span-4">
          <form
            onSubmit={handleSaveUser}
            className="bg-[#0d121d] p-8 rounded-2xl border border-slate-800"
          >
            <h3 className="text-sm font-bold text-white mb-6 uppercase tracking-wider">
              Source Injector
            </h3>
            <div className="space-y-4">
              <input
                className="w-full bg-[#070b14] border border-slate-800 p-3 rounded-lg text-sm text-white"
                placeholder="NAME"
                value={user.name}
                onChange={(e) => setUser({ ...user, name: e.target.value })}
                required
              />
              <input
                className="w-full bg-[#070b14] border border-slate-800 p-3 rounded-lg text-sm text-white"
                placeholder="EMAIL"
                value={user.email}
                onChange={(e) => setUser({ ...user, email: e.target.value })}
                required
              />
              <input
                className="w-full bg-[#070b14] border border-slate-800 p-3 rounded-lg text-sm text-white"
                type="password"
                placeholder="PASSWORD"
                value={user.password}
                onChange={(e) => setUser({ ...user, password: e.target.value })}
                required
              />
              <button
                type="submit"
                className="w-full bg-gradient-to-r from-teal-600 to-blue-600 p-3 rounded-lg text-xs font-bold text-white transition-all"
              >
                ADD_USER
              </button>
            </div>
            {userMsg.text && (
              <p
                className={`mt-4 text-[10px] font-bold uppercase ${userMsg.type === "success" ? "text-teal-400" : "text-red-500"}`}
              >
                {userMsg.text}
              </p>
            )}
          </form>
        </div>

        {/* Right Dashboard */}
        <div className="lg:col-span-8 space-y-8">
          <div className="bg-gradient-to-br from-[#0d121d] to-[#12192b] p-10 rounded-2xl border border-slate-800 text-center">
            <button
              onClick={triggerMigration}
              className="px-8 py-3 border border-slate-700 hover:border-teal-500 rounded-full text-xs font-bold tracking-widest transition-all"
            >
              INITIALIZE_TRANSFER
            </button>
            {migMsg.text && (
              <p className="mt-4 text-[10px] font-bold text-blue-400 uppercase">
                {migMsg.text}
              </p>
            )}
          </div>

          <div className="bg-[#0d121d] p-8 rounded-2xl border border-slate-800">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xs font-bold text-white uppercase tracking-widest">
                Recent Migration Streams
              </h3>
              <input
                className="bg-[#070b14] border border-slate-800 px-4 py-2 rounded-lg text-[10px] w-40 text-slate-400 outline-none focus:border-teal-500"
                placeholder="FILTER_LOGS..."
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>

            {/* Scrollable Table Container */}
            <div className="max-h-[300px] overflow-y-auto scrollbar-thin scrollbar-thumb-slate-700">
              <table className="w-full text-left text-[11px]">
                <thead className="text-slate-600 border-b border-slate-800 sticky top-0 bg-[#0d121d]">
                  <tr>
                    <th className="pb-3">STREAM_ID</th>
                    <th className="pb-3">STATUS</th>
                    <th className="pb-3">TIMESTAMP</th>
                  </tr>
                </thead>
                <tbody className="text-slate-400">
                  {filteredLogs.slice(0, 10).map((log) => (
                    <tr
                      key={log.id}
                      className="border-b border-slate-900 hover:bg-[#12192b]"
                    >
                      <td className="py-3 font-mono text-teal-400">{log.id}</td>
                      <td className="py-3">
                        <span
                          className={`px-2 py-1 rounded text-[9px] font-bold ${log.status === "SUCCESS" ? "text-teal-400 bg-teal-500/10" : "text-red-400 bg-red-500/10"}`}
                        >
                          {log.status}
                        </span>
                      </td>
                      <td className="py-3 font-mono">
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
