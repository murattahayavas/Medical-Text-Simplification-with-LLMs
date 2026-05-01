import { CheckCircle, Activity } from 'lucide-react';
import './Toast.css';

interface ToastProps {
  toast: { message: string; type: 'success' | 'error' } | null;
}

const Toast = ({ toast }: ToastProps) => {
  return (
    <div className={`toast ${toast ? 'show' : ''} ${toast?.type === 'error' ? 'toast-error' : ''}`}>
      {toast?.type === 'success' ? <CheckCircle size={20} /> : <Activity size={20} />}
      {toast?.message}
    </div>
  );
};

export default Toast;
