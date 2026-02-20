import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
    return [
      {
        source: '/api/downloads/:id/:filename',
        destination: `${apiUrl}/api/resumes/download/:id/:filename`,
      },
    ];
  },
};

export default nextConfig;
