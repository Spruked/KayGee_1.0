import ReactDOM from 'react-dom/client';
import { ChakraProvider } from '@chakra-ui/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { KayGeeDashboard } from './components/Dashboard';
import logo from '../../logo.svg';
import './index.css';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

// MAIN DASHBOARD APP
function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ChakraProvider>
        <img src={logo} alt="KayGee 1.0 Logo" style={{ width: '300px', margin: '2rem auto', display: 'block' }} />
        <KayGeeDashboard />
      </ChakraProvider>
    </QueryClientProvider>
  );
}

// CRITICAL: Create root and mount
const root = ReactDOM.createRoot(document.getElementById('root')!);
root.render(<App />);