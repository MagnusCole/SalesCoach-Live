/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: false, // Completamente deshabilitado para evitar problemas de hidratación
  experimental: {
    optimizePackageImports: [],
    reactCompiler: false,
  },
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.resolve.fallback = {
        fs: false,
        net: false,
        tls: false,
        crypto: false,
      };
    }
    return config;
  },
}

module.exports = nextConfig
