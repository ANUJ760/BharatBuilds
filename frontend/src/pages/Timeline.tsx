import { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import ReactFlow, { 
  Node, Edge, Background, Controls, 
  MarkerType, useNodesState, useEdgesState, Position, Handle
} from 'reactflow';
import 'reactflow/dist/style.css';
import dagre from 'dagre';
import { apiGetTimeline, apiRevertToStep } from '../api/client';

// Custom Node Component
const CustomNode = ({ data }: any) => {
  const getIcon = () => {
    switch(data.stepType) {
      case 'clarify': return 'question_answer';
      case 'plan': return 'description';
      case 'codegen': return 'code';
      case 'tool_call': return 'build';
      case 'retry': return 'replay';
      case 'deploy': return 'rocket_launch';
      case 'revert': return 'history';
      default: return 'circle';
    }
  };

  const getStatusColor = () => {
    if (data.status === 'ok') return 'text-green-500 border-green-500';
    if (data.status === 'error') return 'text-red-500 border-red-500';
    if (data.status === 'reverted') return 'text-orange-500 border-orange-500';
    return 'text-gray-500 border-gray-500';
  };

  return (
    <div className={`px-4 py-2 bg-white rounded-xl shadow-lg border-2 ${getStatusColor()} flex flex-col items-center min-w-[150px]`}>
      <Handle type="target" position={Position.Top} className="opacity-0" />
      <span className="material-symbols-outlined mb-1">{getIcon()}</span>
      <span className="font-mono text-xs font-bold uppercase">{data.stepType}</span>
      {data.latencyMs && <span className="text-[10px] text-gray-500">{data.latencyMs}ms</span>}
      <Handle type="source" position={Position.Bottom} className="opacity-0" />
    </div>
  );
};

const nodeTypes = {
  timelineNode: CustomNode,
};

const getLayoutedElements = (nodes: Node[], edges: Edge[], direction = 'TB') => {
  const dagreGraph = new dagre.graphlib.Graph();
  dagreGraph.setDefaultEdgeLabel(() => ({}));
  
  const isHorizontal = direction === 'LR';
  dagreGraph.setGraph({ rankdir: direction, nodesep: 100, edgesep: 50, ranksep: 100 });

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: 150, height: 80 });
  });

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  dagre.layout(dagreGraph);

  nodes.forEach((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);
    node.targetPosition = isHorizontal ? Position.Left : Position.Top;
    node.sourcePosition = isHorizontal ? Position.Right : Position.Bottom;
    node.position = {
      x: nodeWithPosition.x - 150 / 2,
      y: nodeWithPosition.y - 80 / 2,
    };
    return node;
  });

  return { nodes, edges };
};

export const Timeline = () => {
  const { id } = useParams();
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [loading, setLoading] = useState(true);
  const [selectedStep, setSelectedStep] = useState<any>(null);
  const [isReverting, setIsReverting] = useState(false);
  const [revertError, setRevertError] = useState<string | null>(null);
  
  const fetchTimeline = useCallback(async () => {
    if (!id) return;
    try {
      const data = await apiGetTimeline(id);
      
      const rawNodes: Node[] = data.steps.map((step) => ({
        id: step.step_id,
        type: 'timelineNode',
        position: { x: 0, y: 0 },
        data: {
          stepType: step.step_type,
          status: step.status,
          latencyMs: step.latency_ms,
          tokenUsage: step.token_usage,
          hasCodeSnapshot: !!step.code_snapshot,
          errorMessage: step.error_message,
          createdAt: step.created_at,
          // Full data for side panel
          fullData: step
        },
      }));

      const rawEdges: Edge[] = data.steps
        .filter((step: any) => step.parent_step_id)
        .map((step: any) => ({
          id: `${step.parent_step_id}-${step.step_id}`,
          source: step.parent_step_id,
          target: step.step_id,
          animated: step.status === 'ok',
          style: { stroke: '#888', strokeWidth: 2 },
          markerEnd: { type: MarkerType.ArrowClosed, color: '#888' },
        }));

      const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(rawNodes, rawEdges);
      setNodes(layoutedNodes);
      setEdges(layoutedEdges);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [id, setNodes, setEdges]);

  useEffect(() => {
    fetchTimeline();
    // Poll every 5s during active builds
    const interval = setInterval(fetchTimeline, 5000);
    return () => clearInterval(interval);
  }, [fetchTimeline]);

  const onNodeClick = useCallback((_: React.MouseEvent, node: Node) => {
    setSelectedStep(node.data.fullData);
  }, []);

  const handleRevert = async () => {
    if (!id || !selectedStep) return;
    if (!window.confirm("This will redeploy the app to this version. Continue?")) return;

    setIsReverting(true);
    setRevertError(null);
    try {
      if (window.confirm("Revert the live app to this exact state?")) {
        await apiRevertToStep(id, selectedStep.step_id);
        setSelectedStep(null);
        await fetchTimeline();
      }
    } catch (err: any) {
      setRevertError(err.message || 'Failed to revert');
    } finally {
      setIsReverting(false);
    }
  };

  if (loading) return <div className="min-h-screen flex items-center justify-center bg-[#e8e8e8] text-[#111]">Loading...</div>;

  return (
    <motion.div 
      initial={{ opacity: 0 }} 
      animate={{ opacity: 1 }} 
      transition={{ duration: 1.0, ease: [0.22, 1, 0.36, 1] }}
      className="flex flex-col w-full h-screen bg-[#e8e8e8] text-[#111] font-sans relative z-[100]"
    >
      <nav className="fixed top-0 z-50 w-full bg-[#e8e8e8]/80 backdrop-blur-xl border-b border-black/5 px-8 py-4 flex justify-between items-center shadow-sm">
        <Link to={`/apps/${id}`} className="text-sm font-medium flex items-center gap-2 hover:opacity-70 transition-opacity">
          <span className="material-symbols-outlined text-[18px]">arrow_back</span>
          Back to App
        </Link>
        <div className="flex flex-col items-end">
          <div className="flex items-center gap-2 text-[14px] font-medium text-gray-800">
            Decision Timeline
          </div>
          <div className="text-[11px] text-gray-500">Every step taken by the agent is recorded here.</div>
        </div>
      </nav>

      <div className="flex-1 w-full h-full pt-[60px] relative">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onNodeClick={onNodeClick}
          nodeTypes={nodeTypes}
          fitView
          className="bg-transparent"
        >
          <Background color="#ccc" gap={16} />
          <Controls />
        </ReactFlow>

        {/* Side Panel */}
        <AnimatePresence>
          {selectedStep && (
            <motion.div 
              initial={{ x: 400 }}
              animate={{ x: 0 }}
              exit={{ x: 400 }}
              transition={{ type: 'spring', damping: 25, stiffness: 200 }}
              className="absolute right-0 top-0 h-full w-[400px] bg-white border-l border-black/10 shadow-2xl p-6 overflow-y-auto z-40"
            >
              <button 
                onClick={() => setSelectedStep(null)}
                className="absolute top-4 right-4 p-2 rounded-full hover:bg-gray-100 transition-colors"
              >
                <span className="material-symbols-outlined">close</span>
              </button>

              <div className="mt-8 space-y-6">
                <div>
                  <h2 className="text-xl font-semibold uppercase font-mono">{selectedStep.step_type}</h2>
                  <p className="text-sm text-gray-500 mt-1">Status: <span className="font-medium text-black">{selectedStep.status}</span></p>
                </div>

                {selectedStep.reasoning && (
                  <div className="space-y-2">
                    <h3 className="text-xs font-semibold text-gray-500 uppercase">Agent Plan</h3>
                    <div className="p-4 bg-gray-50 rounded-xl text-sm border border-gray-100 overflow-x-auto whitespace-pre-wrap">
                      {selectedStep.reasoning}
                    </div>
                  </div>
                )}

                {selectedStep.code_snapshot && (
                  <div className="space-y-2">
                    <h3 className="text-xs font-semibold text-gray-500 uppercase">Code Diff</h3>
                    <div className="p-4 bg-[#1e1e1e] text-green-400 rounded-xl text-xs font-mono overflow-x-auto max-h-[300px]">
                      <pre>{selectedStep.code_snapshot}</pre>
                    </div>
                  </div>
                )}

                {selectedStep.error_message && (
                  <div className="p-4 bg-red-50 text-red-600 rounded-xl text-sm border border-red-100">
                    <strong>Error:</strong> {selectedStep.error_message}
                  </div>
                )}

                <div className="grid grid-cols-2 gap-4">
                  <div className="p-3 bg-gray-50 rounded-lg border border-gray-100">
                    <div className="text-[10px] text-gray-500 uppercase">Latency</div>
                    <div className="text-sm font-semibold">{selectedStep.latency_ms || 0}ms</div>
                  </div>
                  <div className="p-3 bg-gray-50 rounded-lg border border-gray-100">
                    <div className="text-[10px] text-gray-500 uppercase">Token Usage</div>
                    <div className="text-sm font-semibold">{selectedStep.token_usage || 0}</div>
                  </div>
                </div>

                {selectedStep.code_snapshot && (
                  <div className="pt-4 border-t border-gray-100">
                    {revertError && <div className="text-red-500 text-xs mb-2">{revertError}</div>}
                    <button 
                      onClick={handleRevert}
                      disabled={isReverting}
                      className="w-full py-3 bg-black text-white rounded-xl font-medium flex items-center justify-center gap-2 hover:bg-gray-900 transition-colors disabled:opacity-50"
                    >
                      {isReverting ? (
                        <span className="material-symbols-outlined animate-spin">sync</span>
                      ) : (
                        <span className="material-symbols-outlined">history</span>
                      )}
                      Revert to here
                    </button>
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
};

export default Timeline;
