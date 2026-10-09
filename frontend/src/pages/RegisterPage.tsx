// Register page removed — app uses auto-authentication.
import { Navigate } from 'react-router-dom'
export default function RegisterPage() {
  return <Navigate to="/dashboard" replace />
}
