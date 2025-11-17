/**
 * 📝 EXAMPLE SCRIPT UPLOAD - Frontend Component
 * Allow users to upload quality example scripts
 * System learns from them to generate better scripts
 */

import React, { useState } from 'react';
import { Upload, Zap, BookOpen } from 'lucide-react';
import toast from 'react-hot-toast';

interface ExampleScript {
  id: string;
  name: string;
  content: string;
  type: string;
  hookStyle: string;
  structure: string;
  uploadedAt: string;
}

interface AnalyzedTemplate {
  hookExample: string;
  hookStyle: string;
  setupLength: number;
  riseLength: number;
  climaxLength: number;
  endLength: number;
  tone: string[];
  keyPatterns: string[];
  sentenceVariation: string;
  perspective?: string;  // Server 0 adds this
  pacing?: string;  // Server 0 adds this
  chunkSize?: string;  // Server 0 adds this
  writingTechniques?: string[];  // Server 0 adds this
  uniqueFeatures?: string[];  // Server 0 adds this
}

export const ExampleScriptUpload: React.FC<{
  onScriptSelected: (script: ExampleScript) => void;
  onTemplateExtracted: (template: AnalyzedTemplate) => void;
}> = ({ onScriptSelected, onTemplateExtracted }) => {
  const [exampleScripts, setExampleScripts] = useState<ExampleScript[]>([]);
  const [selectedScript, setSelectedScript] = useState<ExampleScript | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [template, setTemplate] = useState<AnalyzedTemplate | null>(null);
  const [textInput, setTextInput] = useState('');

  /**
   * Upload script file
   */
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const content = event.target?.result as string;
      const newScript: ExampleScript = {
        id: Date.now().toString(),
        name: file.name.replace('.txt', ''),
        content,
        type: 'documentary', // Default, can be changed
        hookStyle: 'researched',
        structure: 'hook-setup-rise-climax-end',
        uploadedAt: new Date().toLocaleString(),
      };

      setExampleScripts([...exampleScripts, newScript]);
      toast.success(`✅ Script uploaded: ${file.name}`);
    };

    reader.readAsText(file);
  };

  /**
   * Add script from text input
   */
  const handleTextSubmit = () => {
    if (!textInput.trim()) {
      toast.error('❌ Please paste a script');
      return;
    }

    const newScript: ExampleScript = {
      id: Date.now().toString(),
      name: `Pasted Script ${exampleScripts.length + 1}`,
      content: textInput,
      type: 'documentary',
      hookStyle: 'researched',
      structure: 'hook-setup-rise-climax-end',
      uploadedAt: new Date().toLocaleString(),
    };

    setExampleScripts([...exampleScripts, newScript]);
    setTextInput('');
    toast.success('✅ Script added to library');
  };

  /**
   * Analyze script structure using backend API
   */
  const analyzeScript = async (script: ExampleScript) => {
    if (!script) return;

    setAnalyzing(true);
    try {
      const response = await fetch('http://localhost:5000/api/analyze-script', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          scriptContent: script.content,
          scriptType: script.type,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to analyze');
      }

      // Check if quota was exceeded and default template was used
      if (data.quotaExceeded) {
        toast.warning('⚠️ Server 0 quota exceeded - using default template. You can still generate videos!', {
          duration: 5000,
        });
      }

      const analyzedTemplate: AnalyzedTemplate = {
        hookExample: data.hookExample || data.hook_example || '',
        hookStyle: data.hookStyle || data.hook_style || 'engaging',
        setupLength: data.setupLength || data.setup_length || 20,
        riseLength: data.riseLength || data.rise_length || 40,
        climaxLength: data.climaxLength || data.climax_length || 30,
        endLength: data.endLength || data.end_length || 10,
        tone: data.tone || [],
        keyPatterns: data.keyPatterns || data.key_patterns || [],
        sentenceVariation: data.sentenceVariation || data.sentence_variation || 'medium',
        perspective: data.perspective,
        pacing: data.pacing,
        chunkSize: data.chunkSize,
        writingTechniques: data.writingTechniques || [],
        uniqueFeatures: data.uniqueFeatures || [],
      };

      setTemplate(analyzedTemplate);
      setSelectedScript(script);
      onScriptSelected(script);
      onTemplateExtracted(analyzedTemplate);

      if (data.quotaExceeded) {
        toast.success('✅ Default template applied - Server 1 ready to generate!');
      } else {
        toast.success('🔬 SERVER 0 extracted template! Server 1 ready to generate!', {
          duration: 4000,
        });
      }
    } catch (error) {
      toast.error(`❌ Analysis failed: ${error}`);
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="bg-gradient-to-br from-slate-900 to-slate-800 p-6 rounded-xl border border-blue-500/30">
      <div className="flex items-center gap-3 mb-6">
        <BookOpen className="text-blue-400" size={24} />
        <h3 className="text-xl font-bold text-white">📚 Example Scripts Library</h3>
        <Zap className="text-yellow-400" size={20} />
      </div>

      {/* Upload Section */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        {/* File Upload */}
        <div className="border-2 border-dashed border-blue-400 rounded-lg p-4 hover:bg-blue-500/10 transition">
          <label className="cursor-pointer flex flex-col items-center gap-2">
            <Upload className="text-blue-400" size={24} />
            <span className="text-sm font-semibold text-blue-300">Upload .txt Script</span>
            <input
              type="file"
              accept=".txt"
              onChange={handleFileUpload}
              className="hidden"
            />
          </label>
        </div>

        {/* Text Input */}
        <div>
          <textarea
            value={textInput}
            onChange={(e) => setTextInput(e.target.value)}
            placeholder="Or paste script here..."
            className="w-full h-24 p-3 bg-slate-700 text-white rounded-lg border border-blue-400/50 focus:border-blue-400 text-sm"
          />
          <button
            onClick={handleTextSubmit}
            className="mt-2 w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg transition"
          >
            ✅ Add Script
          </button>
        </div>
      </div>

      {/* Scripts Library */}
      {exampleScripts.length > 0 && (
        <div className="mb-6">
          <h4 className="text-sm font-semibold text-blue-300 mb-3">📖 Your Scripts ({exampleScripts.length})</h4>
          <div className="grid grid-cols-1 gap-2 max-h-48 overflow-y-auto">
            {exampleScripts.map((script) => (
              <button
                key={script.id}
                onClick={() => analyzeScript(script)}
                disabled={analyzing}
                className={`p-3 rounded-lg text-left transition ${
                  selectedScript?.id === script.id
                    ? 'bg-blue-600 border-2 border-blue-400'
                    : 'bg-slate-700 hover:bg-slate-600 border border-slate-600'
                } ${analyzing ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                <div className="font-semibold text-white">{script.name}</div>
                <div className="text-xs text-gray-300">
                  {script.content.length} chars • {script.uploadedAt}
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Template Display */}
      {template && selectedScript && (
        <div className="bg-slate-700/50 p-4 rounded-lg border border-green-500/30">
          <h4 className="font-bold text-green-300 mb-3">✅ Template Extracted</h4>
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <span className="text-gray-400">Hook Style:</span>
              <div className="text-green-300 font-semibold">{template.hookStyle}</div>
            </div>
            <div>
              <span className="text-gray-400">Sentence Variation:</span>
              <div className="text-green-300 font-semibold">{template.sentenceVariation}</div>
            </div>
            <div>
              <span className="text-gray-400">Setup:</span>
              <div className="text-green-300 font-semibold">~{template.setupLength} words</div>
            </div>
            <div>
              <span className="text-gray-400">Rising Action:</span>
              <div className="text-green-300 font-semibold">~{template.riseLength} words</div>
            </div>
          </div>
          <div className="mt-3 p-2 bg-slate-800 rounded border-l-2 border-green-500">
            <span className="text-xs text-gray-300">Hook Example:</span>
            <p className="text-green-200 text-sm italic mt-1">"{template.hookExample}"</p>
          </div>
          {template.keyPatterns.length > 0 && (
            <div className="mt-3">
              <span className="text-xs text-gray-300">Key Patterns:</span>
              <div className="flex flex-wrap gap-2 mt-2">
                {template.keyPatterns.slice(0, 3).map((pattern, idx) => (
                  <span key={idx} className="text-xs bg-green-900/50 text-green-300 px-2 py-1 rounded">
                    {pattern}
                  </span>
                ))}
              </div>
            </div>
          )}
          <div className="mt-3 p-2 bg-blue-900/30 rounded border-l-2 border-blue-500">
            <p className="text-xs text-blue-200">
              💡 Gemini will now generate scripts following this exact structure and style!
            </p>
          </div>
        </div>
      )}

      {/* Status */}
      {analyzing && (
        <div className="text-center p-4 bg-blue-900/30 rounded-lg border border-blue-500 animate-pulse">
          <div className="inline-block animate-spin text-2xl mb-2">🔬</div>
          <div className="text-blue-200 font-bold text-lg mb-1">
            SERVER 0 Analyzing Template...
          </div>
          <div className="text-blue-300 text-sm">
            Extracting structure, style & patterns with dedicated Server 0
          </div>
          <div className="text-blue-400 text-xs mt-2">
            ✅ Separate API quota - No conflicts with script generation!
          </div>
        </div>
      )}
    </div>
  );
};