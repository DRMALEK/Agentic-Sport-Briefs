import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import { agentAPI, briefsAPI, knowledgeAPI, statsAPI, AgentResponse, Brief, Knowledge } from './api';

interface Message {
  role: 'user' | 'agent';
  content: string;
  agentData?: AgentResponse;
}

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | undefined>();
  const [briefs, setBriefs] = useState<Brief[]>([]);
  const [knowledge, setKnowledge] = useState<Knowledge[]>([]);
  const [stats, setStats] = useState({ total_briefs: 0, total_knowledge: 0, total_conversations: 0 });
  const [showApprovalModal, setShowApprovalModal] = useState(false);
  const [pendingApproval, setPendingApproval] = useState<any>(null);
  const [showKnowledgeModal, setShowKnowledgeModal] = useState(false);
  const [showBriefModal, setShowBriefModal] = useState(false);
  const [selectedBrief, setSelectedBrief] = useState<Brief | null>(null);
  
  // Client-side action states
  const [scoreboard, setScoreboard] = useState<any>(null);
  const [chartData, setChartData] = useState<any>(null);
  const [highlightedKnowledge, setHighlightedKnowledge] = useState<number[]>([]);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadBriefs();
    loadKnowledge();
    loadStats();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadBriefs = async () => {
    try {
      const data = await briefsAPI.getBriefs();
      setBriefs(data.briefs);
    } catch (error) {
      console.error('Failed to load briefs:', error);
    }
  };

  const loadKnowledge = async () => {
    try {
      const data = await knowledgeAPI.getKnowledge();
      setKnowledge(data.knowledge);
    } catch (error) {
      console.error('Failed to load knowledge:', error);
    }
  };

  const loadStats = async () => {
    try {
      const data = await statsAPI.getStats();
      setStats(data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await agentAPI.executeAgent({
        goal: input,
        session_id: sessionId,
        use_knowledge: true,
      });

      setSessionId(response.session_id);

      // CLIENT-SIDE ACTIONS: Process tool results for UI updates
      handleClientActions(response);

      // Check for actions requiring approval
      const requiresApproval = response.tool_calls.some(tc => tc.requires_approval);
      if (requiresApproval) {
        const approvalTool = response.tool_calls.find(tc => tc.requires_approval);
        setPendingApproval(approvalTool);
        setShowApprovalModal(true);
      }

      const agentMessage: Message = {
        role: 'agent',
        content: response.response,
        agentData: response,
      };

      setMessages(prev => [...prev, agentMessage]);
      
      // Reload data if briefs were saved
      if (response.tool_calls.some(tc => tc.tool === 'save_brief')) {
        await loadBriefs();
        await loadStats();
      }
    } catch (error: any) {
      const errorMessage: Message = {
        role: 'agent',
        content: `Error: ${error.message || 'Failed to process request'}`,
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  // CLIENT-SIDE ACTION 1: Update Scoreboard Widget
  // CLIENT-SIDE ACTION 2: Display Statistics Chart
  const handleClientActions = (response: AgentResponse) => {
    response.tool_calls.forEach(toolCall => {
      // Action 1: Update scoreboard from live scores
      if (toolCall.tool === 'fetch_live_scores' && toolCall.result.success) {
        const games = toolCall.result.games;
        if (games && games.length > 0) {
          // Show first live or recent game
          const liveGame = games.find((g: any) => g.status.includes('Live')) || games[0];
          setScoreboard(liveGame);
        }
      }

      // Action 2: Display statistics as interactive chart
      if (toolCall.tool === 'generate_statistics' && toolCall.result.success) {
        const stats = toolCall.result.statistics;
        setChartData(stats);
      }

      // Action 3: Highlight used knowledge items
      if (toolCall.tool === 'search_knowledge' && toolCall.result.success) {
        const resultIds = toolCall.result.results.map((r: any) => r.id);
        setHighlightedKnowledge(resultIds);
        
        // Clear highlight after 3 seconds
        setTimeout(() => setHighlightedKnowledge([]), 3000);
      }
    });
  };

  const handleApproval = async (approved: boolean) => {
    if (!pendingApproval || !sessionId) return;

    try {
      await agentAPI.approveAction(sessionId, 0, approved);
      
      if (approved) {
        // Execute the approved action
        if (pendingApproval.tool === 'save_brief') {
          await loadBriefs();
          await loadStats();
        } else if (pendingApproval.tool === 'export_brief') {
          // Trigger download
          const result = pendingApproval.result;
          if (result.content) {
            const blob = new Blob([result.content], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = result.filename;
            a.click();
            URL.revokeObjectURL(url);
          }
        }
        
        setMessages(prev => [...prev, {
          role: 'agent',
          content: `✓ Action approved and executed: ${pendingApproval.tool}`,
        }]);
      } else {
        setMessages(prev => [...prev, {
          role: 'agent',
          content: `✗ Action rejected: ${pendingApproval.tool}`,
        }]);
      }
    } catch (error) {
      console.error('Approval failed:', error);
    } finally {
      setShowApprovalModal(false);
      setPendingApproval(null);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="App">
      <header className="app-header">
        <div className="header-content">
          <h1 className="app-title">
            <span className="app-title-icon">⚽</span>
            Sports Brief Builder
          </h1>
          <div className="header-stats">
            <div className="stat-item">
              <div className="stat-value">{stats.total_briefs}</div>
              <div className="stat-label">Briefs</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{stats.total_knowledge}</div>
              <div className="stat-label">Knowledge</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{stats.total_conversations}</div>
              <div className="stat-label">Sessions</div>
            </div>
          </div>
        </div>
      </header>

      <div className="main-container">
        <div className="main-content">
          {/* Chat Interface */}
          <div className="card chat-container">
            <h2 className="card-title">💬 Conversation</h2>
            <div className="chat-messages">
              {messages.length === 0 && (
                <div className="empty-state">
                  <div className="empty-state-icon">🤖</div>
                  <p>Start a conversation! Try asking:</p>
                  <ul style={{ textAlign: 'left', display: 'inline-block' }}>
                    <li>"Create a brief about NFL playoffs"</li>
                    <li>"Show me latest basketball scores"</li>
                    <li>"Generate player performance statistics"</li>
                  </ul>
                </div>
              )}
              
              {messages.map((msg, idx) => (
                <div key={idx}>
                  <div className={`message message-${msg.role}`}>
                    <div className="message-header">
                      {msg.role === 'user' ? '👤 You' : '🤖 Agent'}
                    </div>
                    <div className="message-content">{msg.content}</div>
                  </div>

                  {/* Display agent plan and activity */}
                  {msg.agentData && (
                    <>
                      {/* Plan Display */}
                      <div className="plan-display">
                        <strong>📋 Execution Plan:</strong>
                        <ul className="plan-steps">
                          {msg.agentData.plan.steps.map((step, i) => (
                            <li key={i} className="plan-step">{step}</li>
                          ))}
                        </ul>
                      </div>

                      {/* Activity Log */}
                      {msg.agentData.activity_log.length > 0 && (
                        <div className="card">
                          <h3 className="card-title">📊 Activity Trace</h3>
                          <div className="activity-log">
                            {msg.agentData.activity_log.map((activity, i) => (
                              <div
                                key={i}
                                className={`activity-item activity-item-${
                                  activity.status === 'completed' ? 'success' :
                                  activity.status === 'failed' ? 'failed' : 'progress'
                                }`}
                              >
                                <div className="activity-header">
                                  <span className="activity-action">{activity.action}</span>
                                  <span className={`activity-status status-${activity.status}`}>
                                    {activity.status}
                                  </span>
                                </div>
                                {activity.result && (
                                  <div className="activity-result">
                                    {typeof activity.result === 'string' 
                                      ? activity.result 
                                      : JSON.stringify(activity.result, null, 2).substring(0, 200)
                                    }
                                  </div>
                                )}
                                {activity.requires_approval && (
                                  <div className="activity-result" style={{ background: '#fef3c7', color: '#92400e' }}>
                                    ⚠️ This action requires user approval
                                  </div>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Knowledge Used Display */}
                      {msg.agentData.knowledge_used.length > 0 && (
                        <div className="card">
                          <h3 className="card-title">📚 Knowledge Used</h3>
                          <div>
                            {msg.agentData.knowledge_used.map((k, i) => (
                              <span key={i} className="knowledge-badge">
                                {k.source} {k.relevance && `(${k.relevance})`}
                              </span>
                            ))}
                          </div>
                          {msg.agentData.knowledge_used.some(k => k.influence) && (
                            <div className="knowledge-influence">
                              💡 Knowledge base was used to enhance this response with factual sports information
                            </div>
                          )}
                        </div>
                      )}
                    </>
                  )}
                </div>
              ))}
              
              {loading && <div className="loading">Agent is thinking</div>}
              <div ref={messagesEndRef} />
            </div>

            <div className="chat-input-container">
              <input
                type="text"
                className="chat-input"
                placeholder="Ask me to create a sports brief..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                disabled={loading}
              />
              <button
                className="btn btn-primary"
                onClick={handleSend}
                disabled={loading || !input.trim()}
              >
                {loading ? '...' : 'Send'}
              </button>
            </div>
          </div>

          {/* CLIENT ACTION DISPLAYS */}
          {scoreboard && (
            <div className="card">
              <h3 className="card-title">🏆 Live Scoreboard</h3>
              <div className="scoreboard">
                <div className="team">
                  <div className="team-name">{scoreboard.home}</div>
                  <div className="team-score">{scoreboard.home_score}</div>
                </div>
                <div className="score-separator">-</div>
                <div className="team">
                  <div className="team-name">{scoreboard.away}</div>
                  <div className="team-score">{scoreboard.away_score}</div>
                </div>
              </div>
              <div className="game-status">{scoreboard.status} • {scoreboard.date}</div>
            </div>
          )}

          {chartData && (
            <div className="card">
              <h3 className="card-title">📈 Statistics Visualization</h3>
              <div className="stats-chart">
                {chartData.metrics && (
                  <>
                    {Object.entries(chartData.metrics).map(([key, values]: [string, any]) => (
                      <div key={key} className="chart-bar">
                        <div className="chart-label">{key.replace(/_/g, ' ')}</div>
                        <div className="chart-bar-bg">
                          <div 
                            className="chart-bar-fill" 
                            style={{ width: `${Array.isArray(values) ? values[0] * 100 : values}%` }}
                          >
                            {Array.isArray(values) ? values[0].toFixed(1) : values}
                          </div>
                        </div>
                      </div>
                    ))}
                  </>
                )}
                {chartData.average_points && (
                  <>
                    <div className="chart-bar">
                      <div className="chart-label">Points</div>
                      <div className="chart-bar-bg">
                        <div className="chart-bar-fill" style={{ width: `${(chartData.average_points / 50) * 100}%` }}>
                          {chartData.average_points}
                        </div>
                      </div>
                    </div>
                    <div className="chart-bar">
                      <div className="chart-label">Rebounds</div>
                      <div className="chart-bar-bg">
                        <div className="chart-bar-fill" style={{ width: `${(chartData.average_rebounds / 20) * 100}%` }}>
                          {chartData.average_rebounds}
                        </div>
                      </div>
                    </div>
                    <div className="chart-bar">
                      <div className="chart-label">Assists</div>
                      <div className="chart-bar-bg">
                        <div className="chart-bar-fill" style={{ width: `${(chartData.average_assists / 20) * 100}%` }}>
                          {chartData.average_assists}
                        </div>
                      </div>
                    </div>
                  </>
                )}
              </div>
            </div>
          )}
        </div>

        <div className="sidebar">
          {/* Saved Briefs */}
          <div className="card">
            <h3 className="card-title">📝 Saved Briefs</h3>
            <div className="briefs-list">
              {briefs.length === 0 ? (
                <div className="empty-state">
                  <p>No briefs saved yet</p>
                </div>
              ) : (
                briefs.map(brief => (
                  <div
                    key={brief.id}
                    className="brief-item"
                    onClick={() => {
                      setSelectedBrief(brief);
                      setShowBriefModal(true);
                    }}
                  >
                    <div className="brief-title">{brief.title}</div>
                    <div className="brief-meta">
                      <span>{brief.category}</span>
                      <span>{new Date(brief.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Knowledge Base */}
          <div className="card">
            <h3 className="card-title">📚 Knowledge Base</h3>
            <div style={{ marginBottom: '1rem' }}>
              {knowledge.slice(0, 5).map(k => (
                <div
                  key={k.id}
                  className={`knowledge-badge ${highlightedKnowledge.includes(k.id) ? 'highlight-pulse' : ''}`}
                  style={highlightedKnowledge.includes(k.id) ? { background: '#fef3c7', color: '#92400e' } : {}}
                >
                  {k.title}
                </div>
              ))}
            </div>
            <button
              className="btn btn-secondary btn-icon"
              onClick={() => setShowKnowledgeModal(true)}
            >
              + Add Knowledge
            </button>
          </div>
        </div>
      </div>

      {/* Approval Modal */}
      {showApprovalModal && pendingApproval && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h2 className="modal-title">⚠️ Approval Required</h2>
              <button className="modal-close" onClick={() => setShowApprovalModal(false)}>×</button>
            </div>
            <div className="modal-content">
              <p><strong>Action:</strong> {pendingApproval.tool}</p>
              <p><strong>Details:</strong></p>
              <pre style={{ background: '#f9fafb', padding: '1rem', borderRadius: '6px', overflow: 'auto' }}>
                {JSON.stringify(pendingApproval.arguments, null, 2)}
              </pre>
              <p>Do you want to proceed with this action?</p>
            </div>
            <div className="modal-actions">
              <button className="btn btn-danger" onClick={() => handleApproval(false)}>
                Reject
              </button>
              <button className="btn btn-success" onClick={() => handleApproval(true)}>
                Approve
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Knowledge Modal */}
      {showKnowledgeModal && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h2 className="modal-title">Add Knowledge</h2>
              <button className="modal-close" onClick={() => setShowKnowledgeModal(false)}>×</button>
            </div>
            <div className="modal-content">
              <KnowledgeForm
                onSuccess={() => {
                  setShowKnowledgeModal(false);
                  loadKnowledge();
                  loadStats();
                }}
              />
            </div>
          </div>
        </div>
      )}

      {/* Brief Modal */}
      {showBriefModal && selectedBrief && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h2 className="modal-title">{selectedBrief.title}</h2>
              <button className="modal-close" onClick={() => setShowBriefModal(false)}>×</button>
            </div>
            <div className="modal-content">
              <p><strong>Category:</strong> {selectedBrief.category}</p>
              <p><strong>Created:</strong> {new Date(selectedBrief.created_at).toLocaleString()}</p>
              <div style={{ marginTop: '1rem', whiteSpace: 'pre-wrap', lineHeight: '1.6' }}>
                {selectedBrief.content}
              </div>
            </div>
            <div className="modal-actions">
              <button className="btn btn-secondary" onClick={() => setShowBriefModal(false)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Knowledge Form Component
function KnowledgeForm({ onSuccess }: { onSuccess: () => void }) {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [category, setCategory] = useState('general');
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (file) {
        await knowledgeAPI.uploadKnowledge(file);
      } else {
        await knowledgeAPI.createKnowledge({ title, content, category });
      }
      onSuccess();
    } catch (error) {
      console.error('Failed to add knowledge:', error);
      alert('Failed to add knowledge');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="knowledge-form" onSubmit={handleSubmit}>
      <div className="form-group">
        <label className="form-label">Upload File (optional)</label>
        <input
          type="file"
          accept=".txt,.md"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          className="form-input"
        />
        <small style={{ color: '#999' }}>Or fill the form below</small>
      </div>

      <div className="form-group">
        <label className="form-label">Title</label>
        <input
          type="text"
          className="form-input"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required={!file}
          disabled={!!file}
        />
      </div>

      <div className="form-group">
        <label className="form-label">Content</label>
        <textarea
          className="form-textarea"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          required={!file}
          disabled={!!file}
          rows={6}
        />
      </div>

      <div className="form-group">
        <label className="form-label">Category</label>
        <select
          className="form-select"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          disabled={!!file}
        >
          <option value="general">General</option>
          <option value="teams">Teams</option>
          <option value="players">Players</option>
          <option value="stats">Statistics</option>
          <option value="rules">Rules</option>
        </select>
      </div>

      <button type="submit" className="btn btn-primary" disabled={loading}>
        {loading ? 'Adding...' : 'Add Knowledge'}
      </button>
    </form>
  );
}

export default App;
