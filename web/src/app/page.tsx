"use client";
import { useEffect, useState } from "react";

interface Uptime {
  days: number;
  hours: number;
  minutes: number;
  seconds: number;
}

interface HealthcheckResponse {
  message: string;
  uptime: Uptime;
}

export default function Home() {
  const [status, setStatus] = useState<"ok" | "error" | "loading">("loading");
  const [data, setData] = useState<HealthcheckResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [statusCode, setStatusCode] = useState<number | null>(null);

  useEffect(() => {
    const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "";
    fetch(`${baseUrl}/api/v1/healthcheck`)
      .then(async (res) => {
        setStatusCode(res.status);
        if (res.ok) {
          setStatus("ok");
          setData(await res.json());
        } else {
          setStatus("error");
          const err = await res.json();
          setError(err.message || "Unknown error");
        }
      })
      .catch((e) => {
        setStatus("error");
        setError(e.message);
      });
  }, []);

  const renderUptime = (uptime: Uptime) => {
    return `Live since ${uptime.days} days, ${uptime.hours} hours, ${uptime.minutes} minutes`;
  };

  return (
    <main className="min-h-screen flex items-center justify-center bg-gray-950">
      <div className="bg-gray-900 rounded-xl shadow-lg p-8 flex flex-col items-center w-full max-w-md">
        <h1 className="text-3xl font-bold mb-6 text-white">TEMPLATE_PROJECT_NAME</h1>
        {status === "loading" && (
          <div className="text-gray-400">Loading...</div>
        )}
        {status === "ok" && data && (
          <>
            <div className="text-green-400 text-xl font-semibold mb-2">{data.message}</div>
            <div className="text-xs text-gray-300 mt-2">
              {renderUptime(data.uptime)}
            </div>
          </>
        )}
        {status === "error" && (
          <>
            <div className="text-orange-400 text-xl font-semibold mb-2">
              {error || "Error"}
            </div>
            {statusCode && (
              <div className="text-xs text-orange-300 mb-1">Status: {statusCode}</div>
            )}
            {error && (
              <div className="text-xs text-orange-200">{error}</div>
            )}
          </>
        )}
      </div>
    </main>
  );
}
