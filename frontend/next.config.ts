import type { NextConfig } from "next";

// Extract the environment ID from the known frontend URL pattern so this
// config works across environment restarts without hardcoding the full host.
const frontendUrl = process.env.NEXT_PUBLIC_FRONTEND_URL ?? "";
const gitpodHost = frontendUrl.replace(/^https?:\/\//, "");

const nextConfig: NextConfig = {
  // Allow the Gitpod public URL to load Next.js dev resources (JS chunks, HMR).
  // Without this, webpack blocks all cross-origin requests to /_next/* and the
  // app shell loads but no JavaScript executes.
  allowedDevOrigins: [
    gitpodHost,
    "3000--019dd676-8a08-774e-a49c-fe815807db48.us-east-1-01.gitpod.dev",
    "*.gitpod.dev",
  ].filter(Boolean),

  async redirects() {
    return [
      {
        source: "/",
        destination: "/dashboard",
        permanent: false,
      },
    ];
  },
};

export default nextConfig;
