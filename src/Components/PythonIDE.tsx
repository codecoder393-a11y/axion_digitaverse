import { useEffect, useState } from "react";
import { useUser } from "../UserContext";
import { FaPlay, FaSave, FaFolder, FaFile, FaTrash, FaPlus, FaCloudUploadAlt, FaPhoneAlt, FaServer } from "react-icons/fa";
// Lightweight in-app editor (no external editor packages) — provides Tab indentation and simple syntax highlighting overlay

type FileTreeItem = {
  type: "file" | "folder";
  name: string;
  children?: FileTreeItem[];
};

type FileTreeProps = {
  tree: FileTreeItem[];
  onSelect: (path: string) => void;
  selected: string;
  prefix?: string;
};

const sharedStyles = {
  fileItem: {
    textAlign: "left" as const,
    transition: "all 0.3s ease",
    padding: "6px 12px",
    borderRadius: "6px",
    marginBottom: "4px",
    display: "flex",
    alignItems: "center",
    cursor: "pointer",
    color: "rgba(255, 255, 255, 0.8)",
    background: "transparent",
    border: "none",
    width: "100%"
  }
};

function FileTree({ tree, onSelect, selected, prefix = "" }: FileTreeProps) {
  return (
    <ul className="list-unstyled ps-3 mb-0">
      {tree.map((item) =>
        item.type === "folder" ? (
          <li key={prefix + item.name} className="mb-2">
            <div className="d-flex align-items-center text-light-50 mb-1">
              <FaFolder className="me-2 text-warning" />{item.name}
            </div>
            <FileTree tree={item.children || []} onSelect={onSelect} selected={selected} prefix={prefix + item.name + "/"} />
          </li>
        ) : (
          <li key={prefix + item.name}>
            <button
              style={{
                ...sharedStyles.fileItem,
                background: selected === prefix + item.name ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
              }}
              onClick={() => onSelect(prefix + item.name)}
            >
              <FaFile className="me-2 text-info" />{item.name}
            </button>
          </li>
        )
      )}
    </ul>
  );
}

function PythonIDE() {
  const { user } = useUser();
  const [tree, setTree] = useState<any[]>([]);
  const [selected, setSelected] = useState<string>("");
  const [content, setContent] = useState<string>("");
  const [output, setOutput] = useState<string>("");
  const [newPath, setNewPath] = useState("");
  const [refresh, setRefresh] = useState(0);
  const [activeTab, setActiveTab] = useState("files");

  const styles = {
    glassEffect: {
      background: "rgba(33, 37, 41, 0.85)",
      backdropFilter: "blur(10px)",
      borderRadius: "12px",
      border: "1px solid rgba(255, 255, 255, 0.1)",
      boxShadow: "0 8px 32px 0 rgba(31, 38, 135, 0.37)"
    },
    button: {
      background: "rgba(33, 37, 41, 0.5)",
      border: "1px solid rgba(255, 255, 255, 0.1)",
      borderRadius: "8px",
      color: "rgba(255, 255, 255, 0.9)",
      transition: "all 0.3s ease",
      padding: "8px 16px"
    },
    input: {
      background: "rgba(33, 37, 41, 0.3)",
      color: "#fff",
      border: "1px solid rgba(255, 255, 255, 0.1)",
      borderRadius: "8px",
      padding: "8px 12px",
      transition: "all 0.3s ease"
    },
    codeEditor: {
      fontFamily: "monospace",
      fontSize: 15,
      resize: "none" as const,
      height: "auto",
      background: "rgba(33, 37, 41, 0.3)",
      color: "#e9ecef",
      lineHeight: 1.5,
      border: "none",
      padding: "1rem"
    },
    terminal: {
      minHeight: 150,
      background: "rgba(0, 0, 0, 0.3)",
      color: "#50fa7b",
      fontFamily: "monospace",
      padding: 12,
      overflowY: "auto" as const,
      borderTop: "1px solid rgba(255, 255, 255, 0.1)"
    },
    fileItem: {
      textAlign: "left" as const,
      transition: "all 0.3s ease",
      padding: "6px 12px",
      borderRadius: "6px",
      marginBottom: "4px",
      display: "flex",
      alignItems: "center",
      cursor: "pointer",
      color: "rgba(255, 255, 255, 0.8)",
      background: "transparent",
      border: "none",
      width: "100%"
    }
  };

  // Smart Contract State
  const [miners, setMiners] = useState<string[]>([]);
  const [selectedMiner, setSelectedMiner] = useState("");
  const [constructorArgs, setConstructorArgs] = useState("[]");
  const [deployStatus, setDeployStatus] = useState("");
  const [callAddress, setCallAddress] = useState("");
  const [callMethod, setCallMethod] = useState("");
  const [callArgs, setCallArgs] = useState("[]");
  const [callStatus, setCallStatus] = useState("");

  // Fetch file tree
  useEffect(() => {
    fetch("http://127.0.0.1:5001/api/ide/list")
      .then(res => res.json())
      .then(setTree);
  }, [refresh]);

  // Fetch miners
  useEffect(() => {
    fetch("http://127.0.0.1:5001/api/miners")
      .then(res => res.json())
      .then(data => {
        setMiners(data);
        if (data.length > 0) setSelectedMiner(data[0]);
      });
  }, []);

  // Load file content
  useEffect(() => {
    if (selected) {
      fetch("http://127.0.0.1:5001/api/ide/open", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ path: selected }),
      })
        .then(res => res.json())
        .then(data => setContent(data.content || ""));
    } else {
      setContent("");
    }
  }, [selected]);

  const handleSave = () => {
    fetch("http://127.0.0.1:5001/api/ide/save", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ path: selected, content }) })
      .then(() => setOutput(`File ${selected} saved.`));
  };

  const handleRun = () => {
    fetch("http://127.0.0.1:5001/api/ide/run", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ path: selected }) })
      .then(res => res.json())
      .then(data => setOutput(data.output || ""));
  };

  const handleCreate = (isFolder: boolean) => {
    if (!newPath) return;
    fetch("http://127.0.0.1:5001/api/ide/create", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ path: newPath, isFolder }) })
      .then(() => { setNewPath(""); setRefresh(r => r + 1); });
  };

  const handleDelete = () => {
    if (!selected) return;
    fetch("http://127.0.0.1:5001/api/ide/delete", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ path: selected }) })
      .then(() => { setSelected(""); setRefresh(r => r + 1); });
  };

  const handleDeploy = async () => {
    if (!user) { setDeployStatus("You must be logged in to deploy a contract."); return; }
    if (!selected.endsWith(".py")) { setDeployStatus("Please select a Python file to deploy as a contract."); return; }
    setDeployStatus("Deploying...");
    try {
      const args = JSON.parse(constructorArgs);
      const res = await fetch("http://127.0.0.1:5001/api/contract/deploy", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code: content, args, deployer: user.address, miner: selectedMiner }),
      });
      const data = await res.json();
      if (res.ok) {
        setDeployStatus(`Contract deployed successfully! Address: ${data.contract_address}`);
        setCallAddress(data.contract_address);
      } else {
        setDeployStatus(`Error: ${data.error}`);
      }
    } catch (e) {
      setDeployStatus("Invalid constructor arguments. Please provide a valid JSON array.");
    }
  };

  const handleCall = async () => {
    if (!user) { setCallStatus("You must be logged in to call a contract."); return; }
    setCallStatus("Calling method...");
    try {
      const args = JSON.parse(callArgs);
      const res = await fetch("http://127.0.0.1:5001/api/contract/call", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ address: callAddress, method: callMethod, args, caller: user.address, miner: selectedMiner }),
      });
      const data = await res.json();
      if (res.ok) {
        setCallStatus(`Call successful.`);
        setOutput(`Result from ${callMethod}:\n${JSON.stringify(data.result, null, 2)}`);
      } else {
        setCallStatus(`Error: ${data.error}`);
      }
    } catch (e) {
      setCallStatus("Invalid method arguments. Please provide a valid JSON array.");
    }
  };

  // Component styles moved to top

  // Editor helpers: simple Python syntax highlighter (regex-based, lightweight)
  const escapeHtml = (str: string) =>
    str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

  const pythonKeywords = '\\b(?:def|class|import|from|return|if|elif|else|for|while|try|except|finally|with|as|pass|break|continue|lambda|True|False|None|and|or|not|in|is)\\b';

  function highlightCode(src: string) {
    if (!src) return '';
    let out = escapeHtml(src);
    // comments
    out = out.replace(/(#.*?$)/gm, '<span class="cm-comment">$1</span>');
    // strings (single/double/triple)
    out = out.replace(/('''[\s\S]*?'''|"""[\s\S]*?"""|'(?:\\.|[^'\\])*'|"(?:\\.|[^"\\])*")/g, '<span class="cm-string">$1</span>');
    // numbers
    out = out.replace(/\b(0x[0-9a-fA-F]+|\d+\.?\d*|\.\d+)\b/g, '<span class="cm-number">$1</span>');
    // keywords
    out = out.replace(new RegExp(pythonKeywords, 'g'), '<span class="cm-keyword">$&</span>');
    // def/class names
    out = out.replace(/\b(def|class)\s+(\w+)/g, '<span class="cm-keyword">$1</span> <span class="cm-def">$2</span>');
    // operators
    out = out.replace(/(==|!=|<=|>=|\+|\-|\*|\/|%|=|\+=|-=|\*=|\/=|\.|:|\(|\)|\[|\]|\{|\})/g, '<span class="cm-operator">$1</span>');
    return out;
  }

  // Editor keyboard: Tab/Shift+Tab indentation
  function handleEditorKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Tab') {
      e.preventDefault();
      const textarea = e.currentTarget;
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const value = content;
      const tab = '    '; // 4 spaces; change to '\t' if you prefer real tabs

      if (start !== end) {
        // indent/unindent selected lines
        const selected = value.slice(start, end);
        const lines = selected.split('\n');
        if (!e.shiftKey) {
          const replaced = lines.map(l => tab + l).join('\n');
          const newVal = value.slice(0, start) + replaced + value.slice(end);
          setContent(newVal);
          // adjust selection
          textarea.selectionStart = start;
          textarea.selectionEnd = end + tab.length * lines.length;
        } else {
          // unindent
          const replaced = lines.map(l => l.startsWith(tab) ? l.slice(tab.length) : (l.startsWith('\t') ? l.slice(1) : l)).join('\n');
          const removed = lines.reduce((acc, l) => acc + (l.startsWith(tab) ? tab.length : (l.startsWith('\t') ? 1 : 0)), 0);
          const newVal = value.slice(0, start) + replaced + value.slice(end);
          setContent(newVal);
          textarea.selectionStart = start;
          textarea.selectionEnd = Math.max(start, end - removed);
        }
      } else {
        // insert tab at cursor
        const newVal = value.slice(0, start) + tab + value.slice(end);
        setContent(newVal);
        textarea.selectionStart = textarea.selectionEnd = start + tab.length;
      }
    }
  }

  // Scroll sync between textarea and highlight pre
  function syncScroll(e: React.UIEvent<HTMLTextAreaElement>) {
    const wrapper = (e.currentTarget.parentElement as HTMLElement);
    const pre = wrapper?.querySelector('pre') as HTMLElement | null;
    if (pre) {
      pre.scrollTop = e.currentTarget.scrollTop;
      pre.scrollLeft = e.currentTarget.scrollLeft;
    }
  }

  return (
    <div className="d-flex vh-100 bg-dark text-white p-4 gap-4">
      <div className="d-flex flex-column" style={{ width: 300, ...styles.glassEffect }}>
        <div className="nav nav-tabs nav-fill border-0 p-2">
          <button 
            className={`btn ${activeTab === 'files' ? 'btn-primary' : 'btn-outline-primary'} flex-grow-1 me-2`}
            style={styles.button}
            onClick={() => setActiveTab('files')}
          >
            <FaFolder className="me-2" /> Files
          </button>
          <button 
            className={`btn ${activeTab === 'contracts' ? 'btn-primary' : 'btn-outline-primary'} flex-grow-1`}
            style={styles.button}
            onClick={() => setActiveTab('contracts')}
          >
            <FaServer className="me-2" /> Contracts
          </button>
        </div>
        <div className="p-3 overflow-auto flex-grow-1">
          {activeTab === 'files' && (
            <div>
              <div className="mb-4" style={{ ...styles.glassEffect, padding: '15px' }}>
                <FileTree tree={tree} onSelect={setSelected} selected={selected} />
              </div>
              <div style={{ ...styles.glassEffect, padding: '15px' }}>
                <div className="input-group mb-3">
                  <input 
                    className="form-control bg-dark text-light border-0" 
                    style={{ borderRadius: '8px' }}
                    placeholder="path/to/file.py" 
                    value={newPath} 
                    onChange={e => setNewPath(e.target.value)} 
                  />
                </div>
                <button 
                  className="btn btn-outline-primary w-100 mb-2" 
                  style={{ borderRadius: '8px', transition: 'all 0.3s ease' }}
                  onClick={() => handleCreate(false)}
                >
                  <FaPlus className="me-2"/>Create File
                </button>
                <button 
                  className="btn btn-outline-secondary w-100 mb-2" 
                  style={{ borderRadius: '8px', transition: 'all 0.3s ease' }}
                  onClick={() => handleCreate(true)}
                >
                  <FaFolder className="me-2"/>Create Folder
                </button>
                <button 
                  className="btn btn-outline-danger w-100" 
                  style={{ borderRadius: '8px', transition: 'all 0.3s ease' }}
                  onClick={handleDelete} 
                  disabled={!selected}
                >
                  <FaTrash className="me-2"/>Delete Selected
                </button>
              </div>
            </div>
          )}
          {activeTab === 'contracts' && (
            <div className="px-2">
              {!user ? (
                <div style={{ ...styles.glassEffect, padding: '20px', textAlign: 'center' }}>
                  <div className="alert alert-warning border-0" style={{ background: 'rgba(255, 193, 7, 0.1)' }}>
                    Please log in to interact with contracts.
                  </div>
                </div>
              ) : (
                <div>
                  <div style={{ ...styles.glassEffect, padding: '20px', marginBottom: '20px' }}>
                    <h5 className="text-success d-flex align-items-center">
                      <FaCloudUploadAlt className="me-2"/>
                      <span>Deploy Contract</span>
                    </h5>
                    <p className="small text-light-50">Deploy the code in the current editor to the blockchain.</p>
                    <div className="mb-3">
                      <label className="form-label small text-light-50">Constructor Args (JSON)</label>
                      <input 
                        className="form-control bg-dark text-light border-0" 
                        style={{ borderRadius: '8px' }}
                        value={constructorArgs} 
                        onChange={e => setConstructorArgs(e.target.value)} 
                      />
                    </div>
                    <div className="mb-3">
                      <label className="form-label small text-light-50">
                        <FaServer className="me-2"/>Miner
                      </label>
                      <select 
                        className="form-select bg-dark text-light border-0" 
                        style={{ borderRadius: '8px' }}
                        value={selectedMiner} 
                        onChange={e => setSelectedMiner(e.target.value)} 
                        disabled={miners.length === 0}
                      >
                        {miners.length > 0 ? 
                          miners.map(m => <option key={m} value={m}>{m.substring(0,10)}...{m.substring(m.length-10)}</option>) : 
                          <option>No miners registered</option>
                        }
                      </select>
                    </div>
                    <button 
                      className="btn btn-success w-100" 
                      style={{ borderRadius: '8px', transition: 'all 0.3s ease' }}
                      onClick={handleDeploy}
                    >
                      Deploy
                    </button>
                    {deployStatus && (
                      <div 
                        className="alert alert-info border-0 mt-3" 
                        style={{ 
                          background: 'rgba(13, 202, 240, 0.1)',
                          borderRadius: '8px'
                        }}
                      >
                        {deployStatus}
                      </div>
                    )}
                  </div>

                  <div style={{ ...styles.glassEffect, padding: '20px' }}>
                    <h5 className="text-info d-flex align-items-center"><FaPhoneAlt className="me-2"/>Call Contract Method</h5>
                    <div className="mb-2">
                      <label className="form-label small">Contract Address</label>
                      <input className="form-control form-control-sm" value={callAddress} onChange={e => setCallAddress(e.target.value)} />
                    </div>
                    <div className="mb-2">
                      <label className="form-label small">Method Name</label>
                      <input className="form-control form-control-sm" value={callMethod} onChange={e => setCallMethod(e.target.value)} />
                    </div>
                    <div className="mb-2">
                      <label className="form-label small">Method Args (JSON)</label>
                      <input className="form-control form-control-sm" value={callArgs} onChange={e => setCallArgs(e.target.value)} />
                    </div>
                    <div className="mb-3">
                      <label className="form-label small"><FaServer className="me-2"/>Miner</label>
                      <select className="form-select form-select-sm" value={selectedMiner} onChange={e => setSelectedMiner(e.target.value)} disabled={miners.length === 0}>
                        {miners.length > 0 ? miners.map(m => <option key={m} value={m}>{m.substring(0,10)}...{m.substring(m.length-10)}</option>) : <option>No miners registered</option>}
                      </select>
                    </div>
                    <button className="btn btn-info w-100" onClick={handleCall}>Call Method</button>
                    {callStatus && <div className="alert alert-info small mt-2 p-2">{callStatus}</div>}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
      
      <div className="flex-grow-1 d-flex flex-column" style={styles.glassEffect}>
        <div className="d-flex align-items-center p-3 border-bottom border-secondary">
          <span className="fw-bold me-auto">{selected || "No file selected"}</span>
          <button
            className="btn btn-success btn-sm me-2"
            style={{ ...styles.button, background: 'rgba(25, 135, 84, 0.2)' }}
            onClick={handleSave}
            disabled={!selected}
          >
            <FaSave className="me-2" />Save
          </button>
          <button
            className="btn btn-primary btn-sm"
            style={{ ...styles.button, background: 'rgba(13, 110, 253, 0.2)' }}
            onClick={handleRun}
            disabled={!selected || !selected.endsWith(".py")}
          >
            <FaPlay className="me-2" />Run
          </button>
        </div>
        <div style={{ flexGrow: 1, minHeight: 200, position: 'relative' }} className="editor-wrapper">
          {/* Highlight layer (read-only) */}
          <pre
            aria-hidden
            className="cm-editor"
            style={{
              position: 'absolute',
              inset: 0,
              margin: 0,
              padding: styles.codeEditor.padding,
              overflow: 'auto',
              pointerEvents: 'none',
              whiteSpace: 'pre',
            }}
            dangerouslySetInnerHTML={{ __html: highlightCode(content) }}
          />

          {/* Transparent textarea on top to capture input */}
          <textarea
            className="form-control flex-grow-1 border-0"
            style={{
              ...styles.codeEditor,
              position: 'relative',
              background: 'transparent',
              color: 'transparent',
              caretColor: styles.codeEditor.color,
              zIndex: 2,
            }}
            value={content}
            onChange={e => setContent(e.target.value)}
            onKeyDown={handleEditorKeyDown}
            onScroll={e => syncScroll(e)}
            disabled={!selected}
            placeholder="Select a file or create a new one to start coding..."
          />
        </div>
        <div style={styles.terminal}>
          <b className="text-white">Output:</b>
          <pre className="m-0">{output}</pre>
        </div>
      </div>
    </div>
  );
}

export default PythonIDE;
