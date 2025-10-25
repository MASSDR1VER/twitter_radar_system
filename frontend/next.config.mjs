/** @type {import('next').NextConfig} */
const nextConfig = {
  // output: 'export',  // Temporarily disabled for dynamic routes
  // trailingSlash: true,
  output: 'standalone',  // For Docker deployment
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
}

export default nextConfig
