import { useState, useEffect, useCallback, useRef, Suspense } from 'react';
import {
  Box, VStack, HStack, Text, Button, Textarea, useToast,
  Stat, StatLabel, StatNumber, StatHelpText, StatArrow,
  Badge, Tabs, TabList, TabPanels, Tab, TabPanel, Card,
  CardHeader, CardBody, Heading, SimpleGrid, CircularProgress,
  CircularProgressLabel, IconButton, Tooltip, Modal,
  ModalOverlay, ModalContent, ModalHeader, ModalBody,
  ModalCloseButton, Skeleton, Fade, ScaleFade, Code,
  FormControl, FormLabel, Switch, Select, Alert,
  AlertIcon, Spinner, Progress, Checkbox, Input
} from '@chakra-ui/react';
import { LineChart, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, Area } from 'recharts';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { create } from 'zustand';
import { FiRefreshCw, FiFilter, FiZap, FiTrendingUp } from 'react-icons/fi';
import { ErrorBoundary } from 'react-error-boundary';
import { orbLearningGraph } from '../lib/OrbLearningGraph';
import { PresenceStore } from '../store/presenceStore';
import { KayGeeOrb } from './Orb';
import { useWebSocket } from '../hooks/useWebSocket';

// Types
interface CognitiveComponent {
  initialized: boolean;
  status: Record<string, any>;
  last_update: number;
  error_count: number;
  confidence_score: number;
}

interface CognitiveStatus {
  status: 'online' | 'degraded' | 'error';
  session_id: string;
  interaction_count: number;
  components: Record<string, CognitiveComponent>;
  active_reasoning_threads: number;
  memory_consolidation_queue: number;
  timestamp: number;
}

interface HealthComponent {
  health_score: number;
  healthy: boolean;
  latency_ms: number;
  last_check: number;
  circuit_breaker: 'open' | 'closed' | 'half_open';
}

interface HealthStatus {
  overall_health: number;
  components: Record<string, HealthComponent>;
  timestamp: number;
  trend: 'up' | 'down' | 'stable';
}

interface AdversarialTrial {
  id: string;
  name: string;
  success: boolean;
  duration_ms: number;
  timestamp: number;
  skeptic_contribution: number;
  synthesis_confidence: number;
  error?: string;
  reasoning_path: string[];
}

interface QueryHistoryItem {
  id: string;
  query: string;
  response: string;
  confidence: number;
  processing_time_ms: number;
  timestamp: number;
  reasoning_depth: number;
}

interface WSMessage {
  type: 'cognitive_update' | 'trial_complete' | 'log_entry' | 'health_alert';
  data: any;
  timestamp: number;
}

// Store
interface DashboardStore {
  queryHistory: QueryHistoryItem[];
  addToHistory: (item: QueryHistoryItem) => void;
  selectedComponent: string | null;
  setSelectedComponent: (comp: string | null) => void;
  timeRange: '1h' | '6h' | '24h';
  setTimeRange: (range: '1h' | '6h' | '24h') => void;
}

const useDashboardStore = create<DashboardStore>()(
  (set) => ({
    queryHistory: [],
    addToHistory: (item) => set((state) => ({ 
      queryHistory: [item, ...state.queryHistory].slice(0, 100) 
    })),
    selectedComponent: null,
    setSelectedComponent: (comp) => set({ selectedComponent: comp }),
    timeRange: '1h',
    setTimeRange: (range) => set({ timeRange: range }),
  })
);

// API Client
declare global {
  interface ImportMeta {
    env: Record<string, string>;
  }
}

const API_BASE = (import.meta as any).env.VITE_API_URL || 'http://localhost:8001';

const apiClient = {
  async fetchCognitiveStatus(signal?: AbortSignal): Promise<CognitiveStatus> {
    const res = await fetch(`${API_BASE}/api/cognitive/status`, { signal });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  },
  
  async fetchHealthStatus(signal?: AbortSignal): Promise<HealthStatus> {
    const res = await fetch(`${API_BASE}/api/health/detailed`, { signal });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  },
  
  async fetchTrials(limit = 50, signal?: AbortSignal): Promise<AdversarialTrial[]> {
    const res = await fetch(`${API_BASE}/api/adversarial/trials?limit=${limit}`, { signal });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return data.trials || [];
  },

  async fetchSummaries(signal?: AbortSignal): Promise<{ filename: string; size: number; modified: string }[]> {
    const res = await fetch(`${API_BASE}/api/adversarial/summaries`, { signal });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return data.summaries || [];
  },

  async fetchSummary(filename: string, signal?: AbortSignal): Promise<string> {
    const res = await fetch(`${API_BASE}/api/adversarial/summary/${encodeURIComponent(filename)}`, { signal });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return data.content || '';
  },

  async fetchLogs(signal?: AbortSignal): Promise<string[]> {
    const res = await fetch(`${API_BASE}/api/logs/recent?lines=50`, { signal });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return data.logs || [];
  },
  
  async queryKayGee(text: string, signal?: AbortSignal): Promise<{ 
    text: string; 
    confidence: number; 
    processing_time_ms: number;
    reasoning_path: string[];
    skeptic_checks: number;
  }> {
    const res = await fetch(`${API_BASE}/speak`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
      signal
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  }
};

// Helper functions
const getHealthColor = (health: number) => {
  if (health >= 0.8) return 'green';
  if (health >= 0.6) return 'yellow';
  return 'red';
};

const getStatusBadge = (status: string) => {
  const colorScheme = status === 'online' ? 'green' : status === 'error' ? 'red' : 'yellow';
  return <Badge colorScheme={colorScheme}>{status.toUpperCase()}</Badge>;
};

// Components
function ComponentDetailModal({ isOpen, onClose, componentName, component }: {
  isOpen: boolean;
  onClose: () => void;
  componentName: string;
  component: CognitiveComponent;
}) {
  return (
    <Modal isOpen={isOpen} onClose={onClose} size="xl">
      <ModalOverlay />
      <ModalContent bg="gray.800" color="white">
        <ModalHeader>{componentName.toUpperCase()}</ModalHeader>
        <ModalCloseButton />
        <ModalBody pb={6}>
          <VStack align="stretch" spacing={4}>
            <Stat>
              <StatLabel>Confidence Score</StatLabel>
              <StatNumber>{(component.confidence_score * 100).toFixed(1)}%</StatNumber>
            </Stat>
            <Stat>
              <StatLabel>Error Count</StatLabel>
              <StatNumber color={component.error_count > 0 ? 'red.400' : 'green.400'}>
                {component.error_count}
              </StatNumber>
            </Stat>
            <Box>
              <Text fontSize="sm" color="gray.400" mb={2}>Status Object</Text>
              <Code p={3} borderRadius="md" maxH="200px" overflow="auto">
                {JSON.stringify(component.status, null, 2)}
              </Code>
            </Box>
          </VStack>
        </ModalBody>
      </ModalContent>
    </Modal>
  );
}

function HealthTrendChart({ timeRange }: { timeRange: string }) {
  const { data: metrics, isLoading } = useQuery({
    queryKey: ['healthMetrics', timeRange],
    queryFn: async ({ signal }) => {
      const res = await fetch(`${API_BASE}/api/health/history?range=${timeRange}`, { signal });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return res.json();
    },
    staleTime: 30000
  });

  if (isLoading) return <Skeleton h="200px" />;

  return (
    <ResponsiveContainer width="100%" height={200}>
      <LineChart data={metrics}>
        <CartesianGrid strokeDasharray="3 3" stroke="#4A5568" />
        <XAxis dataKey="timestamp" stroke="#A0AEC0" />
        <YAxis stroke="#A0AEC0" />
        <RechartsTooltip contentStyle={{ backgroundColor: '#2D3748', border: 'none' }} />
        <Area type="monotone" dataKey="overall_health" stroke="#38B2AC" fill="#38B2AC" fillOpacity={0.3} />
      </LineChart>
    </ResponsiveContainer>
  );
}

// Main Component
export function KayGeeDashboard() {
  const toast = useToast();
  const queryClient = useQueryClient();
  const { selectedComponent, setSelectedComponent, queryHistory, addToHistory, timeRange, setTimeRange } = useDashboardStore();
  
  const [queryText, setQueryText] = useState('');
  const [enableSkepticMode, setEnableSkepticMode] = useState(true);
  const [logFilters, setLogFilters] = useState({ level: '', component: '' });
  const [selectedSummary, setSelectedSummary] = useState<string | null>(null);
  const [summaryContent, setSummaryContent] = useState<string>('');

  // Single response state
  const [response, setResponse] = useState<{
    text: string;
    confidence: number;
    processingTime: number;
    reasoningDepth: number;
    skepticChecks: number;
  } | null>(null);

  // KayGeeOrb is rendered below

  const wsUrl = API_BASE.replace(/^http/, 'ws') + '/ws';
  const { isConnected } = useWebSocket(wsUrl, useCallback((msg: WSMessage) => {
    switch (msg.type) {
      case 'cognitive_update':
        queryClient.setQueryData(['cognitiveStatus'], msg.data.cognitive_status);
        queryClient.setQueryData(['healthStatus'], msg.data.health_status);
        break;
      case 'trial_complete':
        queryClient.invalidateQueries({ queryKey: ['trials'] });
        break;
      case 'health_alert':
        toast({
          title: "Health Alert",
          description: msg.data.message,
          status: "warning",
          duration: 5000
        });
        break;
    }
  }, [queryClient, toast]));

  // React Query hooks
  const { data: cognitiveStatus } = useQuery({
    queryKey: ['cognitiveStatus'],
    queryFn: () => apiClient.fetchCognitiveStatus(),
    staleTime: 60000,
    refetchInterval: 30000,
  });

  const { data: healthStatus } = useQuery({
    queryKey: ['healthStatus'],
    queryFn: () => apiClient.fetchHealthStatus(),
    staleTime: 30000,
    refetchInterval: 15000,
  });

  const { data: trials } = useQuery({
    queryKey: ['trials', timeRange],
    queryFn: () => apiClient.fetchTrials(),
    staleTime: 120000,
  });

  const { data: summaries } = useQuery({
    queryKey: ['summaries'],
    queryFn: () => apiClient.fetchSummaries(),
    staleTime: 120000,
  });

  const { data: logs = [] } = useQuery({
    queryKey: ['logs', logFilters],
    queryFn: () => apiClient.fetchLogs(),
    staleTime: 30000,
  });

  // UI controls
  const [hidePhilosophers, setHidePhilosophers] = useState(true);
  const [presenceState, setPresenceState] = useState(PresenceStore.get());
  const [selectedSummary, setSelectedSummary] = useState<string | null>(null);
  const [summaryContent, setSummaryContent] = useState<string>('');

  useEffect(() => {
    // Subscribe to PresenceStore updates if available
    const unsub = PresenceStore.subscribe ? PresenceStore.subscribe(() => {
      try { setPresenceState(PresenceStore.get()); } catch (e) {}
    }) : () => {};
    return unsub;
  }, []);

  // Query handler
  const handleQuery = useCallback(async () => {
    if (!queryText.trim()) return;

    const startTime = performance.now();
    
    try {
      const result = await apiClient.queryKayGee(queryText);
      const processingTime = performance.now() - startTime;
      
      setResponse({
        text: result.text,
        confidence: result.confidence,
        processingTime,
        reasoningDepth: result.reasoning_path.length,
        skepticChecks: result.skeptic_checks
      });

      addToHistory({
        id: crypto.randomUUID(),
        query: queryText,
        response: result.text,
        confidence: result.confidence,
        processing_time_ms: processingTime,
        timestamp: Date.now(),
        reasoning_depth: result.reasoning_path.length
      });

      setQueryText('');

    } catch (error: any) {
      toast({
        title: "Query Failed",
        description: error.message,
        status: "error",
        duration: 5000
      });
    }
  }, [queryText, addToHistory, toast]);

  // Prepare component list, with optional philosopher filtering
  const philosopherNames = ['locke', 'hume', 'kant', 'spinoza', 'taleb'];
  const componentsEntries = cognitiveStatus?.components ? Object.entries(cognitiveStatus.components) : [];
  const displayedComponents = componentsEntries.filter(([name]) => !(hidePhilosophers && philosopherNames.includes(name.toLowerCase())));

  return (
    <ErrorBoundary fallback={<Alert status="error"><AlertIcon />Dashboard crashed</Alert>}>
      <Suspense fallback={<Spinner size="xl" />}>
        <Box p={6} minH="100vh" bg="gray.800">
          {/* Header */}
          <VStack spacing={6} align="stretch">
            <HStack justify="space-between" align="flex-start">
              <VStack align="start" spacing={2}>
                <Heading size="xl" bgGradient="linear(to-r, cyan.400, purple.500)" bgClip="text">
                  🧠 KayGee Cognitive Operating System
                </Heading>
                <Text color="gray.400" fontSize="sm">
                  Autonomous Reasoning Platform v2.1 | Live Debugging Interface
                </Text>
                <HStack spacing={3} mt={2}>
                  <Badge colorScheme={isConnected ? 'green' : 'red'}>
                    WS: {isConnected ? 'Live' : 'Reconnecting...'}
                  </Badge>
                  <Badge colorScheme="blue">
                    Threads: {cognitiveStatus?.active_reasoning_threads || 0}
                  </Badge>
                  <Badge colorScheme="purple">
                    Queue: {cognitiveStatus?.memory_consolidation_queue || 0}
                  </Badge>
                </HStack>
              </VStack>

              <HStack spacing={4}>
                <FormControl display="flex" alignItems="center" width="auto">
                  <FormLabel mb="0" fontSize="sm" mr={3}>Range:</FormLabel>
                  <Select size="sm" value={timeRange} onChange={(e) => setTimeRange(e.target.value as any)}>
                    <option value="1h">Last Hour</option>
                    <option value="6h">Last 6 Hours</option>
                    <option value="24h">Last 24 Hours</option>
                  </Select>
                </FormControl>
                <FormControl display="flex" alignItems="center" width="auto">
                  <FormLabel mb="0" fontSize="sm" mr={3}>Hide Philosophers</FormLabel>
                  <Switch isChecked={hidePhilosophers} onChange={(e) => setHidePhilosophers(e.target.checked)} />
                </FormControl>
                
                <Tooltip label="Force refresh all data">
                  <IconButton
                    aria-label="Refresh"
                    icon={<FiRefreshCw />}
                    onClick={() => queryClient.invalidateQueries()}
                  />
                </Tooltip>
              </HStack>
            </HStack>

            {/* System Health */}
            {healthStatus && (
              <Fade in={true}>
                <Card bg="gray.800" borderColor="gray.700">
                  <CardHeader>
                    <HStack justify="space-between">
                      <VStack align="start">
                        <Heading size="md">System Health</Heading>
                        <Text fontSize="sm" color="gray.400">
                          Trend: {healthStatus.trend === 'up' ? '📈' : healthStatus.trend === 'down' ? '📉' : '➡️'} {timeRange}
                        </Text>
                      </VStack>
                      <CircularProgress
                        value={healthStatus.overall_health * 100}
                        color={getHealthColor(healthStatus.overall_health)}
                        size="80px"
                      >
                        <CircularProgressLabel>
                          {(healthStatus.overall_health * 100).toFixed(0)}%
                        </CircularProgressLabel>
                      </CircularProgress>
                    </HStack>
                  </CardHeader>
                  <CardBody>
                    <SimpleGrid columns={{ base: 2, md: 6 }} spacing={4}>
                      {Object.entries(healthStatus.components).map(([name, comp]) => (
                        <Box key={name} textAlign="center" p={3} bg="gray.700" borderRadius="md">
                          <Tooltip label={`Latency: ${comp.latency_ms}ms`}>
                            <VStack spacing={1}>
                              <Text fontSize="xs" color="gray.400">{name.toUpperCase()}</Text>
                              <CircularProgress
                                value={comp.health_score * 100}
                                color={comp.healthy ? 'green.400' : 'red.400'}
                                size="45px"
                              >
                                <CircularProgressLabel fontSize="xs">
                                  {comp.health_score > 0.8 ? 'OK' : comp.health_score > 0.5 ? 'WARN' : 'FAIL'}
                                </CircularProgressLabel>
                              </CircularProgress>
                              <Text fontSize="xs" color="gray.500">{comp.latency_ms}ms</Text>
                            </VStack>
                          </Tooltip>
                        </Box>
                      ))}
                    </SimpleGrid>
                    <Box mt={6}>
                      <HealthTrendChart timeRange={timeRange} />
                    </Box>
                  </CardBody>
                </Card>
              </Fade>
            )}

            {/* Monitoring: Orb + Space Field */}
            <Fade in={true}>
              <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4} mt={4}>
                <Card bg="gray.800" borderColor="gray.700">
                  <CardHeader>
                    <HStack justify="space-between">
                      <Heading size="sm">Orb Monitor</Heading>
                      <HStack spacing={2}>
                        <Button size="sm" colorScheme="teal" onClick={async () => {
                          try {
                            const res = await fetch(`${API_BASE}/api/stabilize`, { method: 'POST' });
                            if (!res.ok) throw new Error(`HTTP ${res.status}`);
                            toast({ title: 'Stabilize requested', status: 'success', duration: 3000 });
                          } catch (e: any) {
                            toast({ title: 'Stabilize failed', description: e?.message || String(e), status: 'error' });
                          }
                        }}>Stabilize</Button>
                        <Button size="sm" onClick={() => { orbLearningGraph.reset(); toast({ title: 'Orb learning reset', status: 'info' }); }}>Reset Learning</Button>
                        <Button size="sm" onClick={() => {
                          try {
                            const data = orbLearningGraph.exportLearning();
                            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
                            const url = URL.createObjectURL(blob);
                            const a = document.createElement('a');
                            a.href = url; a.download = 'orb_learning.json'; a.click();
                            URL.revokeObjectURL(url);
                            toast({ title: 'Export started', status: 'success' });
                          } catch (e: any) {
                            toast({ title: 'Export failed', description: String(e), status: 'error' });
                          }
                        }}>Export</Button>
                      </HStack>
                    </HStack>
                  </CardHeader>
                  <CardBody>
                    <VStack align="stretch">
                      <HStack spacing={4}>
                        <Text fontSize="sm">Visibility:</Text>
                        <Badge colorScheme={presenceState?.visibility === 'manifested' ? 'purple' : presenceState?.visibility === 'latent' ? 'gray' : 'blue'}>
                          {presenceState?.visibility}
                        </Badge>
                        <Text fontSize="sm">Resonance:</Text>
                        <Text fontWeight="bold">{Math.round((presenceState?.resonance || 0) * 100)}%</Text>
                      </HStack>

                      <Box height="1px" bg="gray.700" my={2} />

                      <HStack spacing={6}>
                        <Box>
                          <Text fontSize="xs" color="gray.400">Learned Confidence</Text>
                          <Text fontWeight="bold">{(orbLearningGraph.getStats().confidence * 100).toFixed(1)}%</Text>
                        </Box>
                        <Box>
                          <Text fontSize="xs" color="gray.400">Total Interactions</Text>
                          <Text fontWeight="bold">{orbLearningGraph.getStats().totalInteractions}</Text>
                        </Box>
                        <Box>
                          <Text fontSize="xs" color="gray.400">Learned Zones</Text>
                          <Text fontWeight="bold">{orbLearningGraph.getStats().learnedZones}</Text>
                        </Box>
                        <Box>
                          <Text fontSize="xs" color="gray.400">Avg Distance</Text>
                          <Text fontWeight="bold">{Math.round(orbLearningGraph.getStats().averageDistance)}</Text>
                        </Box>
                      </HStack>

                      <HStack spacing={6} mt={3}>
                        <Box>
                          <Text fontSize="xs" color="gray.400">Times Summoned</Text>
                          <Text fontWeight="bold">{orbLearningGraph.getStats().summonedCount}</Text>
                        </Box>
                        <Box>
                          <Text fontSize="xs" color="gray.400">Path Crossed</Text>
                          <Text fontWeight="bold">{orbLearningGraph.getStats().pathCrossedCount}</Text>
                        </Box>
                        <Box>
                          <Text fontSize="xs" color="gray.400">Success Rate</Text>
                          <Text fontWeight="bold">
                            {orbLearningGraph.getStats().totalInteractions > 0 
                              ? ((orbLearningGraph.getStats().pathCrossedCount / orbLearningGraph.getStats().totalInteractions) * 100).toFixed(1) + '%'
                              : '0%'
                            }
                          </Text>
                        </Box>
                        <Box>
                          <Text fontSize="xs" color="gray.400">Last Updated</Text>
                          <Text fontWeight="bold" fontSize="xs">{orbLearningGraph.getStats().lastUpdated}</Text>
                        </Box>
                      </HStack>
                    </VStack>
                  </CardBody>
                </Card>

                {/* Space Field Controls removed from here; displayed at top of dashboard */}
              </SimpleGrid>
            </Fade>

            {/* Tabs */}
            <Tabs variant="soft-rounded" colorScheme="cyan">
              <TabList>
                <Tab><HStack spacing={2}><FiZap /><Text>Reasoning Core</Text></HStack></Tab>
                <Tab><HStack spacing={2}><FiTrendingUp /><Text>Metrics</Text></HStack></Tab>
                <Tab>🧪 Adversarial Trials</Tab>
                <Tab>📝 System Logs</Tab>
                <Tab>💬 Query Interface</Tab>
              </TabList>

              <TabPanels>
                {/* Reasoning Core */}
                <TabPanel>
                  <VStack spacing={6} align="stretch">
                    <Card bg="gray.800" borderColor="cyan.600">
                      <CardHeader>
                        <Heading size="sm">Active Reasoning Threads</Heading>
                      </CardHeader>
                      <CardBody>
                        <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4}>
                          <Stat>
                            <StatLabel>Max Depth</StatLabel>
                            <StatNumber color="cyan.400">5</StatNumber>
                          </Stat>
                          <Stat>
                            <StatLabel>Active Threads</StatLabel>
                            <StatNumber>{cognitiveStatus?.active_reasoning_threads || 0}</StatNumber>
                          </Stat>
                          <Stat>
                            <StatLabel>Avg Confidence</StatLabel>
                            <StatNumber>0.87</StatNumber>
                          </Stat>
                        </SimpleGrid>
                      </CardBody>
                    </Card>
                    
                    <Box>
                      <Heading size="md" mb={4}>SKG Components</Heading>
                      <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
                        {displayedComponents.map(([name, comp]) => (
                          <ScaleFade key={name} initialScale={0.9} in={true}>
                            <Card 
                              bg="gray.800" 
                              borderColor={comp.initialized ? 'green.600' : 'red.600'}
                              cursor="pointer"
                              onClick={() => {
                                setSelectedComponent(name);
                              }}
                              _hover={{ borderColor: 'cyan.500' }}
                            >
                              <CardBody>
                                <HStack justify="space-between" mb={3}>
                                  <Text fontWeight="bold" fontSize="sm">{name.toUpperCase()}</Text>
                                  {getStatusBadge(comp.initialized ? 'online' : 'offline')}
                                </HStack>
                                <VStack align="stretch" spacing={2}>
                                  <Progress 
                                    value={comp.confidence_score * 100} 
                                    size="sm" 
                                    colorScheme="cyan"
                                    borderRadius="full"
                                  />
                                  <HStack justify="space-between" fontSize="xs">
                                    <Text color="gray.400">Confidence</Text>
                                    <Text>{(comp.confidence_score * 100).toFixed(0)}%</Text>
                                  </HStack>
                                  {comp.error_count > 0 && (
                                    <Text fontSize="xs" color="red.300">
                                      {comp.error_count} errors
                                    </Text>
                                  )}
                                </VStack>
                              </CardBody>
                            </Card>
                          </ScaleFade>
                        ))}
                      </SimpleGrid>
                    </Box>
                  </VStack>
                </TabPanel>

                {/* Metrics */}
                <TabPanel>
                  <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
                    <Card bg="gray.800" borderColor="gray.700">
                      <CardHeader>
                        <Heading size="sm">Vault Performance</Heading>
                      </CardHeader>
                      <CardBody>
                        <Stat>
                          <StatLabel>APriori Hit Rate</StatLabel>
                          <StatNumber>94.2%</StatNumber>
                          <StatHelpText>
                            <StatArrow type="increase" /> +2%
                          </StatHelpText>
                        </Stat>
                      </CardBody>
                    </Card>
                    
                    <Card bg="gray.800" borderColor="gray.700">
                      <CardHeader>
                        <Heading size="sm">Tribunal Activity</Heading>
                      </CardHeader>
                      <CardBody>
                        <Stat>
                          <StatLabel>Skeptic Overrides</StatLabel>
                          <StatNumber color="orange.300">12</StatNumber>
                          <StatHelpText>Last hour</StatHelpText>
                        </Stat>
                      </CardBody>
                    </Card>
                    
                    <Card bg="gray.800" borderColor="gray.700">
                      <CardHeader>
                        <Heading size="sm">Memory System</Heading>
                      </CardHeader>
                      <CardBody>
                        <Stat>
                          <StatLabel>Consolidation Rate</StatLabel>
                          <StatNumber>98.1%</StatNumber>
                        </Stat>
                      </CardBody>
                    </Card>
                    
                    <Card bg="gray.800" borderColor="gray.700">
                      <CardHeader>
                        <Heading size="sm">Query Performance</Heading>
                      </CardHeader>
                      <CardBody>
                        <Stat>
                          <StatLabel>Avg Response</StatLabel>
                          <StatNumber>2.3s</StatNumber>
                        </Stat>
                      </CardBody>
                    </Card>
                  </SimpleGrid>
                </TabPanel>

                {/* Trials */}
                <TabPanel>
                  <VStack align="stretch" spacing={4}>
                    <HStack justify="space-between">
                      <Heading size="md">Adversarial Trial Results</Heading>
                      <HStack>
                        <Checkbox 
                          isChecked={enableSkepticMode} 
                          onChange={(e) => setEnableSkepticMode(e.target.checked)}
                        >
                          Enable Live Skepticism
                        </Checkbox>
                        <Badge colorScheme="purple">{trials?.length || 0} trials</Badge>
                        <Button size="sm" colorScheme="orange" onClick={async () => {
                          try {
                            toast({ title: 'Running adversarial suite...', status: 'info' });
                            const res = await fetch(`${API_BASE}/api/adversarial/run`, { method: 'POST' });
                            if (!res.ok) throw new Error(`HTTP ${res.status}`);
                            const data = await res.json();
                            queryClient.invalidateQueries({ queryKey: ['trials'] });
                            toast({ title: 'Adversarial run complete', description: `${data.trials?.length || 0} trials`, status: 'success', duration: 4000 });
                          } catch (e: any) {
                            toast({ title: 'Adversarial run failed', description: e?.message || String(e), status: 'error' });
                          }
                        }}>Run Suite</Button>
                        <Button size="sm" colorScheme="blue" onClick={() => {
                          if (!trials || trials.length === 0) {
                            toast({ title: 'No results to export', status: 'warning' });
                            return;
                          }
                          const dataStr = JSON.stringify({ trials, timestamp: Date.now() }, null, 2);
                          const dataBlob = new Blob([dataStr], { type: 'application/json' });
                          const url = URL.createObjectURL(dataBlob);
                          const link = document.createElement('a');
                          link.href = url;
                          link.download = `adversarial_trials_${new Date().toISOString().split('T')[0]}.json`;
                          document.body.appendChild(link);
                          link.click();
                          document.body.removeChild(link);
                          URL.revokeObjectURL(url);
                          toast({ title: 'Results exported', status: 'success' });
                        }}>Export Results</Button>
                    </HStack>

                    {trials && trials.length > 0 ? (
                      <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
                        {trials.slice(0, 9).map((trial) => (
                          <Fade key={trial.id} in={true}>
                            <Card 
                              bg="gray.800" 
                              borderColor={trial.success ? 'green.600' : 'red.600'}
                              opacity={trial.success ? 1 : 0.8}
                            >
                              <CardHeader>
                                <HStack justify="space-between">
                                  <Heading size="sm" isTruncated>{trial.name}</Heading>
                                  <Badge colorScheme={trial.success ? 'green' : 'red'}>
                                    {trial.success ? 'PASS' : 'FAIL'}
                                  </Badge>
                                </HStack>
                              </CardHeader>
                              <CardBody>
                                <VStack align="stretch" spacing={2} fontSize="sm">
                                  <HStack justify="space-between">
                                    <Text color="gray.400">Duration:</Text>
                                    <Text fontFamily="mono">{(trial.duration_ms / 1000).toFixed(2)}s</Text>
                                  </HStack>
                                  <HStack justify="space-between">
                                    <Text color="gray.400">Skeptic:</Text>
                                    <Text fontFamily="mono">{trial.skeptic_contribution.toFixed(2)}</Text>
                                  </HStack>
                                  <HStack justify="space-between">
                                    <Text color="gray.400">Synthesis:</Text>
                                    <Text fontFamily="mono">{trial.synthesis_confidence.toFixed(2)}</Text>
                                  </HStack>
                                  {trial.reasoning_path && (
                                    <Box mt={2}>
                                      <Text fontSize="xs" color="gray.500">Path:</Text>
                                      <Text fontSize="xs" fontFamily="mono" color="gray.300">
                                        {trial.reasoning_path.join(' → ')}
                                      </Text>
                                    </Box>
                                  )}
                                  {trial.error && (
                                    <Code colorScheme="red" fontSize="xs" p={2} borderRadius="md">
                                      {trial.error}
                                    </Code>
                                  )}
                                </VStack>
                              </CardBody>
                            </Card>
                          </Fade>
                        ))}
                      </SimpleGrid>
                    ) : (
                      <Alert status="info">
                        <AlertIcon />
                        No trials available
                      </Alert>
                    )}

                    {/* View Reports Section */}
                    <Box mt={6}>
                      <Heading size="md" mb={4}>Trial Reports</Heading>
                      {summaries && summaries.length > 0 ? (
                        <VStack align="stretch" spacing={3}>
                          {summaries.map((summary) => (
                            <Card key={summary.filename} bg="gray.800" borderColor="gray.700">
                              <CardBody>
                                <HStack justify="space-between" align="center">
                                  <VStack align="start" spacing={1}>
                                    <Text fontWeight="bold" fontSize="sm">{summary.filename}</Text>
                                    <HStack spacing={4} fontSize="xs" color="gray.400">
                                      <Text>Size: {(summary.size / 1024).toFixed(1)} KB</Text>
                                      <Text>Modified: {new Date(summary.modified).toLocaleString()}</Text>
                                    </HStack>
                                  </VStack>
                                  <Button 
                                    size="sm" 
                                    colorScheme="blue" 
                                    onClick={async () => {
                                      try {
                                        const content = await apiClient.fetchSummary(summary.filename);
                                        setSummaryContent(content);
                                        setSelectedSummary(summary.filename);
                                      } catch (e: any) {
                                        toast({ title: 'Failed to load report', description: e?.message || String(e), status: 'error' });
                                      }
                                    }}
                                  >
                                    View Report
                                  </Button>
                                </HStack>
                              </CardBody>
                            </Card>
                          ))}
                        </VStack>
                      ) : (
                        <Alert status="info">
                          <AlertIcon />
                          No reports available
                        </Alert>
                      )}
                    </Box>
                  </VStack>
                </TabPanel>

                {/* Logs */}
                <TabPanel>
                  <Card bg="gray.800" borderColor="gray.700">
                    <CardHeader>
                      <HStack justify="space-between">
                        <Heading size="md">Live System Logs</Heading>
                        <HStack spacing={2}>
                          <Input 
                            placeholder="Filter logs..." 
                            size="sm" 
                            width="200px"
                            onChange={(e) => setLogFilters(prev => ({ ...prev, level: e.target.value }))}
                          />
                          <IconButton 
                            aria-label="Filter" 
                            icon={<FiFilter />} 
                            size="sm" 
                          />
                        </HStack>
                      </HStack>
                    </CardHeader>
                    <CardBody>
                      <Box maxH="500px" overflowY="auto" fontFamily="mono" fontSize="xs" bg="gray.900" p={3} borderRadius="md">
                        {logs.filter(log => log.includes(logFilters.level)).map((log, idx) => {
                          const isError = log.includes('ERROR');
                          const isWarning = log.includes('WARN');
                          return (
                            <Text 
                              key={idx} 
                              color={isError ? 'red.300' : isWarning ? 'yellow.300' : 'gray.300'}
                              fontSize="xs"
                              mb={1}
                            >
                              {log}
                            </Text>
                          );
                        })}
                      </Box>
                    </CardBody>
                  </Card>
                </TabPanel>

                {/* Query Interface */}
                <TabPanel>
                  <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6}>
                    <Card bg="gray.800" borderColor="gray.700">
                      <CardHeader>
                        <Heading size="md">Query KayGee</Heading>
                      </CardHeader>
                      <CardBody>
                        <VStack spacing={4} align="stretch">
                          <Textarea
                            placeholder="Enter query for autonomous processing..."
                            value={queryText}
                            onChange={(e) => setQueryText(e.target.value)}
                            bg="gray.700"
                            color="white"
                            border="none"
                            _focus={{ bg: "gray.600", borderColor: "cyan.500" }}
                            minH="150px"
                            resize="vertical"
                          />
                          <HStack justify="space-between">
                            <FormControl display="flex" alignItems="center" width="auto">
                              <FormLabel mb="0" fontSize="sm" mr={2}>Skeptic Mode:</FormLabel>
                              <Switch 
                                isChecked={enableSkepticMode}
                                onChange={(e) => setEnableSkepticMode(e.target.checked)}
                              />
                            </FormControl>
                            <Button
                              colorScheme="cyan"
                              onClick={handleQuery}
                              isLoading={false}
                              loadingText="Reasoning..."
                              rightIcon={<FiZap />}
                              isDisabled={!queryText.trim()}
                            >
                              Execute Query
                            </Button>
                          </HStack>
                        </VStack>
                      </CardBody>
                    </Card>

                    <Card bg="gray.800" borderColor="gray.700">
                      <CardHeader>
                        <Heading size="md">Response & Metadata</Heading>
                      </CardHeader>
                      <CardBody>
                        {response ? (
                          <VStack align="stretch" spacing={4}>
                            <Box>
                              <Text fontSize="sm" color="gray.400" mb={2}>Response:</Text>
                              <Text whiteSpace="pre-wrap" fontSize="sm" lineHeight="tall">
                                {response.text}
                              </Text>
                            </Box>
                            <SimpleGrid columns={2} spacing={4}>
                              <Stat>
                                <StatLabel>Confidence</StatLabel>
                                <StatNumber>{(response.confidence * 100).toFixed(1)}%</StatNumber>
                              </Stat>
                              <Stat>
                                <StatLabel>Processing Time</StatLabel>
                                <StatNumber>{(response.processingTime / 1000).toFixed(2)}s</StatNumber>
                              </Stat>
                              <Stat>
                                <StatLabel>Reasoning Depth</StatLabel>
                                <StatNumber>{response.reasoningDepth}</StatNumber>
                              </Stat>
                              <Stat>
                                <StatLabel>Skeptic Checks</StatLabel>
                                <StatNumber>{response.skepticChecks}</StatNumber>
                              </Stat>
                            </SimpleGrid>
                          </VStack>
                        ) : (
                          <Text color="gray.500" fontStyle="italic">
                            Execute a query to see response metadata...
                          </Text>
                        )}
                      </CardBody>
                    </Card>
                  </SimpleGrid>

                  {/* Query History */}
                  <Box mt={6}>
                    <Heading size="sm" mb={3}>Recent Queries ({queryHistory.length})</Heading>
                    <VStack align="stretch" spacing={2} maxH="300px" overflowY="auto">
                      {queryHistory.slice(0, 5).map((q) => (
                        <Card key={q.id} bg="gray.800" borderColor="gray.700" size="sm">
                          <HStack justify="space-between" p={3}>
                            <VStack align="start" spacing={0}>
                              <Text fontSize="sm" isTruncated maxW="400px">{q.query}</Text>
                              <Text fontSize="xs" color="gray.500">
                                {new Date(q.timestamp).toLocaleTimeString()} | 
                                {(q.processing_time_ms / 1000).toFixed(2)}s | 
                                Depth: {q.reasoning_depth}
                              </Text>
                            </VStack>
                            <CircularProgress 
                              value={q.confidence * 100} 
                              size="30px"
                              color={q.confidence > 0.8 ? 'green.400' : 'yellow.400'}
                            >
                              <CircularProgressLabel fontSize="xs">
                                {(q.confidence * 100).toFixed(0)}
                              </CircularProgressLabel>
                            </CircularProgress>
                          </HStack>
                        </Card>
                      ))}
                    </VStack>
                  </Box>
                </TabPanel>
              </TabPanels>
            </Tabs>
          </VStack>

          {/* Component Detail Modal */}
          {selectedComponent && cognitiveStatus?.components[selectedComponent] && (
            <ComponentDetailModal
              isOpen={!!selectedComponent}
              onClose={() => setSelectedComponent(null)}
              componentName={selectedComponent}
              component={cognitiveStatus.components[selectedComponent]}
            />
          )}

          {/* Summary Modal */}
          <Modal isOpen={!!selectedSummary} onClose={() => setSelectedSummary(null)} size="6xl">
            <ModalOverlay />
            <ModalContent bg="gray.800" color="white" maxH="80vh">
              <ModalHeader>{selectedSummary}</ModalHeader>
              <ModalCloseButton />
              <ModalBody pb={6} overflowY="auto">
                <Code 
                  as="pre" 
                  whiteSpace="pre-wrap" 
                  fontSize="sm" 
                  p={4} 
                  borderRadius="md" 
                  bg="gray.900"
                  maxH="60vh"
                  overflowY="auto"
                >
                  {summaryContent}
                </Code>
              </ModalBody>
            </ModalContent>
          </Modal>

          {/* KayGee Orb (Three.js) */}
          <KayGeeOrb />
        </Box>
      </Suspense>
    </ErrorBoundary>
  );
}