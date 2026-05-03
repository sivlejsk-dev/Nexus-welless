/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  },
  images: {
    unoptimized: false,
    domains: ['localhost'],
  },
  output: 'standalone',
}

module.exports = nextConfig
