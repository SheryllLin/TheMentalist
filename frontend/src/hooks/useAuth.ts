// Auth is handled automatically by the API client (auto-login with demo credentials).
// This hook is kept as a no-op stub so any lingering import doesn't break the build.
export function useAuth() {
  return {
    user: null,
    isAuthenticated: true,
    login: async () => {},
    register: async () => {},
    logout: () => {},
  }
}
