/**
 * GeoGov Lite Frontend Application
 * Production-grade compliance analysis interface
 */

class GeoGovApp {
    constructor() {
        this.apiBase = 'http://localhost:8000/api';
        this.currentView = 'single-analysis';
        this.analysisResults = [];
        this.systemHealth = null;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.checkSystemHealth();
        this.loadSettings();
        
        // Initialize tooltips and other UI components
        setTimeout(() => this.updateSystemStatus(), 1000);
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const view = e.currentTarget.dataset.view;
                if (view) this.switchView(view);
            });
        });

        // Modal handlers
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.closeModal(e.target.id);
            }
        });

        // Form handlers
        document.getElementById('analyze-btn').addEventListener('click', () => this.analyzeFeature());
        document.getElementById('bulk-analyze-btn').addEventListener('click', () => this.runBulkAnalysis());

        // Input method switching
        document.querySelectorAll('input[name="input-method"]').forEach(radio => {
            radio.addEventListener('change', () => this.switchInputMethod());
        });

        // File upload
        document.getElementById('csv-file').addEventListener('change', (e) => this.handleFileUpload(e));

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyboardShortcuts(e));
    }

    switchView(viewName) {
        // Update navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-view="${viewName}"]`).classList.add('active');

        // Update content
        document.querySelectorAll('.view').forEach(view => {
            view.classList.remove('active');
        });
        document.getElementById(viewName).classList.add('active');

        this.currentView = viewName;

        // Load view-specific data
        this.loadViewData(viewName);
    }

    async loadViewData(viewName) {
        switch (viewName) {
            case 'results':
                await this.loadDashboardData();
                break;
            case 'corpus':
                await this.loadCorpusStatus();
                break;
            case 'audit':
                await this.loadAuditTrail();
                break;
        }
    }

    // API Methods
    async makeRequest(endpoint, options = {}) {
        const url = `${this.apiBase}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            }
        };

        try {
            const response = await fetch(url, { ...defaultOptions, ...options });
            
            if (!response.ok) {
                const error = await response.text();
                throw new Error(`HTTP ${response.status}: ${error}`);
            }

            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            } else {
                return response;
            }
        } catch (error) {
            this.showNotification(`API Error: ${error.message}`, 'error');
            throw error;
        }
    }

    async checkSystemHealth() {
        try {
            this.systemHealth = await this.makeRequest('/health');
            this.updateSystemStatus();
        } catch (error) {
            this.systemHealth = { ok: false, error: error.message };
            this.updateSystemStatus();
        }
    }

    updateSystemStatus() {
        const statusElement = document.getElementById('system-status');
        const indicator = statusElement.querySelector('.status-indicator');
        const text = statusElement.querySelector('span');

        if (this.systemHealth?.ok) {
            indicator.className = 'status-indicator healthy';
            text.textContent = 'System Healthy';
        } else {
            indicator.className = 'status-indicator error';
            text.textContent = 'System Error';
        }
    }

    // Feature Analysis
    async analyzeFeature() {
        const button = document.getElementById('analyze-btn');
        
        // Collect form data directly from elements
        const featureData = {
            feature_id: document.getElementById('feature_id').value.trim(),
            title: document.getElementById('title').value.trim(),
            description: document.getElementById('description').value.trim(),
            docs: this.parseCommaSeparated(document.getElementById('docs').value),
            tags: this.parseCommaSeparated(document.getElementById('tags').value),
            code_hints: this.parseCommaSeparated(document.getElementById('code_hints').value)
        };
        
        // Validate required fields
        const requiredFields = ['feature_id', 'title', 'description'];
        const missing = requiredFields.filter(field => !featureData[field]);
        
        if (missing.length > 0) {
            this.showNotification(`Please fill in required fields: ${missing.join(', ')}`, 'error');
            return;
        }

        try {
            button.disabled = true;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
            
            this.showLoading('Analyzing feature for compliance requirements...');

            const result = await this.makeRequest('/analyze', {
                method: 'POST',
                body: JSON.stringify(featureData)
            });

            this.hideLoading();
            this.displayAnalysisResult(result);
            this.analysisResults.push(result);
            
            this.showNotification('Feature analysis completed successfully', 'success');

        } catch (error) {
            this.hideLoading();
            this.showNotification(`Analysis failed: ${error.message}`, 'error');
        } finally {
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-search"></i> Analyze Feature';
        }
    }

    displayAnalysisResult(result) {
        const resultsSection = document.getElementById('analysis-results');
        const resultsContent = document.getElementById('results-content');

        const complianceClass = result.needs_geo_compliance ? 'required' : 'not-required';
        const complianceText = result.needs_geo_compliance ? 'COMPLIANCE REQUIRED' : 'NO COMPLIANCE NEEDED';
        const complianceIcon = result.needs_geo_compliance ? 'fa-exclamation-triangle' : 'fa-check-circle';

        resultsContent.innerHTML = `
            <div class="result-card">
                <div class="result-header">
                    <div>
                        <h3>${result.feature_id}: ${result.title || 'Feature Analysis'}</h3>
                        <div class="result-meta">
                            <span class="compliance-badge ${complianceClass}">
                                <i class="fas ${complianceIcon}"></i>
                                ${complianceText}
                            </span>
                            <span class="confidence-score">Confidence: ${(result.confidence * 100).toFixed(1)}%</span>
                        </div>
                    </div>
                </div>
                
                <div class="result-details">
                    <div class="detail-section">
                        <h4>Reasoning</h4>
                        <p>${result.reasoning}</p>
                    </div>
                    
                    ${result.regulations && result.regulations.length > 0 ? `
                        <div class="detail-section">
                            <h4>Applicable Regulations</h4>
                            <ul>
                                ${result.regulations.map(reg => `<li><code>${reg}</code></li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                    
                    ${result.signals && result.signals.length > 0 ? `
                        <div class="detail-section">
                            <h4>Detected Signals</h4>
                            <div class="signal-tags">
                                ${result.signals.map(signal => `<span class="signal-tag">${signal}</span>`).join('')}
                            </div>
                        </div>
                    ` : ''}
                    
                    ${result.citations && result.citations.length > 0 ? `
                        <div class="detail-section">
                            <h4>Citations</h4>
                            ${result.citations.map(citation => `
                                <div class="citation">
                                    <strong>Source:</strong> ${citation.source}<br>
                                    <em>${citation.snippet}</em>
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}
                    
                    <div class="result-metadata">
                        <small class="text-muted">
                            Analysis ID: ${result.hash} | 
                            Policy Version: ${result.policy_version} | 
                            Timestamp: ${new Date(result.ts).toLocaleString()}
                            ${result.matched_rules && result.matched_rules.length > 0 ? 
                                ` | Rules: ${result.matched_rules.join(', ')}` : ''}
                        </small>
                    </div>
                </div>
            </div>
        `;

        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    // Bulk Analysis
    async runBulkAnalysis() {
        const textarea = document.getElementById('bulk_features');
        const button = document.getElementById('bulk-analyze-btn');
        
        let featuresData;
        try {
            featuresData = JSON.parse(textarea.value);
            if (!Array.isArray(featuresData)) {
                throw new Error('Features must be an array');
            }
        } catch (error) {
            this.showNotification(`Invalid JSON: ${error.message}`, 'error');
            return;
        }

        try {
            button.disabled = true;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
            
            this.showBulkProgress();
            this.updateProgress(0, 'Initializing bulk analysis...');

            // Simulate progress updates
            const progressInterval = setInterval(() => {
                const progress = Math.min(90, document.getElementById('progress-fill').style.width.replace('%', '') * 1 + 10);
                this.updateProgress(progress, `Processing features... ${progress}%`);
            }, 500);

            const result = await this.makeRequest('/bulk_analyze', {
                method: 'POST',
                body: JSON.stringify({ items: featuresData })
            });

            clearInterval(progressInterval);
            this.updateProgress(100, 'Analysis complete!');

            setTimeout(() => {
                this.displayBulkResults(result);
                this.showNotification(`Bulk analysis completed: ${result.count} features processed`, 'success');
            }, 1000);

        } catch (error) {
            this.showNotification(`Bulk analysis failed: ${error.message}`, 'error');
            document.getElementById('bulk-progress').style.display = 'none';
        } finally {
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-play"></i> Run Bulk Analysis';
        }
    }

    showBulkProgress() {
        document.getElementById('bulk-progress').style.display = 'block';
    }

    updateProgress(percentage, text) {
        document.getElementById('progress-fill').style.width = `${percentage}%`;
        document.getElementById('progress-text').textContent = text;
        document.getElementById('progress-percentage').textContent = `${percentage.toFixed(0)}%`;
    }

    displayBulkResults(result) {
        const resultsSection = document.getElementById('bulk-results');
        const resultsContent = document.getElementById('bulk-results-content');

        resultsContent.innerHTML = `
            <div class="bulk-summary">
                <h4>Analysis Summary</h4>
                <p><strong>${result.count}</strong> features analyzed</p>
                <p>Results exported to: <code>${result.csv_path}</code></p>
                
                <div class="bulk-actions">
                    <button class="btn btn-primary" onclick="app.downloadCSV()">
                        <i class="fas fa-download"></i>
                        Download CSV Results
                    </button>
                    <button class="btn btn-secondary" onclick="app.downloadEvidence()">
                        <i class="fas fa-file-archive"></i>
                        Download Evidence ZIP
                    </button>
                </div>
            </div>
        `;

        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    // Dashboard Data
    async loadDashboardData() {
        // This would typically load from your analysis results
        // For now, we'll use mock data based on current session
        const totalAnalyses = this.analysisResults.length;
        const complianceRequired = this.analysisResults.filter(r => r.needs_geo_compliance).length;
        const avgConfidence = totalAnalyses > 0 ? 
            this.analysisResults.reduce((sum, r) => sum + r.confidence, 0) / totalAnalyses : 0;

        document.getElementById('total-analyses').textContent = totalAnalyses;
        document.getElementById('compliance-required').textContent = complianceRequired;
        document.getElementById('no-compliance').textContent = totalAnalyses - complianceRequired;
        document.getElementById('avg-confidence').textContent = (avgConfidence * 100).toFixed(1) + '%';

        this.displayRecentResults();
    }

    displayRecentResults() {
        const container = document.getElementById('recent-results-table');
        
        if (this.analysisResults.length === 0) {
            container.innerHTML = '<p>No recent analyses found</p>';
            return;
        }

        const recentResults = this.analysisResults.slice(-10).reverse();
        
        container.innerHTML = `
            <table>
                <thead>
                    <tr>
                        <th>Feature ID</th>
                        <th>Compliance</th>
                        <th>Confidence</th>
                        <th>Regulations</th>
                        <th>Timestamp</th>
                    </tr>
                </thead>
                <tbody>
                    ${recentResults.map(result => `
                        <tr>
                            <td><code>${result.feature_id}</code></td>
                            <td>
                                <span class="compliance-badge ${result.needs_geo_compliance ? 'required' : 'not-required'}">
                                    ${result.needs_geo_compliance ? 'Required' : 'Not Required'}
                                </span>
                            </td>
                            <td>${(result.confidence * 100).toFixed(1)}%</td>
                            <td>${result.regulations.join(', ') || 'None'}</td>
                            <td>${new Date(result.ts).toLocaleString()}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }

    // Corpus Management
    async loadCorpusStatus() {
        try {
            const status = await this.makeRequest('/rag_status');
            
            document.getElementById('docs-indexed').textContent = status.chunks_available || 0;
            document.getElementById('vector-status').textContent = 
                status.vectorstore_available ? 'Active' : 'Inactive';
            document.getElementById('last-updated').textContent = 'Unknown';
            
        } catch (error) {
            this.showNotification(`Failed to load corpus status: ${error.message}`, 'error');
        }
    }

    async refreshCorpus() {
        try {
            this.showLoading('Refreshing knowledge base...');
            
            const result = await this.makeRequest('/refresh_corpus', {
                method: 'POST'
            });
            
            this.hideLoading();
            this.showNotification(`Knowledge base refreshed: ${result.ingested} documents indexed`, 'success');
            this.loadCorpusStatus();
            
        } catch (error) {
            this.hideLoading();
            this.showNotification(`Failed to refresh corpus: ${error.message}`, 'error');
        }
    }

    // Export Functions
    async downloadEvidence() {
        try {
            this.showLoading('Generating evidence package...');
            
            const response = await this.makeRequest('/evidence');
            const blob = await response.blob();
            
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `geogov-evidence-${new Date().toISOString().split('T')[0]}.zip`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            this.hideLoading();
            this.showNotification('Evidence package downloaded successfully', 'success');
            
        } catch (error) {
            this.hideLoading();
            this.showNotification(`Failed to download evidence: ${error.message}`, 'error');
        }
    }

    async downloadCSV() {
        // This would typically download the actual CSV from the server
        // For now, we'll generate one from current results
        if (this.analysisResults.length === 0) {
            this.showNotification('No analysis results to export', 'warning');
            return;
        }

        const csvContent = this.generateCSV(this.analysisResults);
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `compliance-analysis-${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        this.showNotification('CSV exported successfully', 'success');
    }

    generateCSV(results) {
        const headers = ['feature_id', 'title', 'needs_geo_compliance', 'reasoning', 'regulations', 'confidence', 'signals', 'matched_rules', 'policy_version', 'ts'];
        
        const rows = results.map(result => [
            result.feature_id,
            '', // title not stored in results
            result.needs_geo_compliance,
            `"${result.reasoning}"`,
            result.regulations.join(';'),
            result.confidence,
            result.signals.join(';'),
            result.matched_rules.join(';'),
            result.policy_version,
            result.ts
        ]);

        return [headers, ...rows].map(row => row.join(',')).join('\n');
    }

    // Utility Functions
    parseCommaSeparated(value) {
        return value ? value.split(',').map(s => s.trim()).filter(s => s) : [];
    }

    loadExampleFeature() {
        const examples = {
            feature_id: 'F-2381',
            title: 'Personalized Home Feed v3',
            description: 'Reranks videos using watch history and user preferences. Planned rollout to EU markets with personalized recommendation algorithms. Uses machine learning to customize content based on user behavior and viewing patterns.',
            docs: 'https://internal/prd, https://internal/trd',
            tags: 'recommender, personalization, minors_possible',
            code_hints: 'uses ageGate(), if region in ["EU","EEA"]:'
        };

        Object.keys(examples).forEach(key => {
            const element = document.getElementById(key);
            if (element) element.value = examples[key];
        });

        this.showNotification('Example feature loaded', 'success');
    }

    loadBulkTemplate() {
        const template = [
            {
                feature_id: "F-2381",
                title: "Personalized Home Feed v3",
                description: "Reranks videos using watch history; EU rollout planned.",
                docs: ["https://internal/prd"],
                tags: ["recommender", "personalization", "minors_possible"],
                code_hints: ["uses ageGate()", "if region in ['EU','EEA']:"]
            },
            {
                feature_id: "F-1205",
                title: "Smart Ad Targeting",
                description: "Behavioral targeting system for relevant ads with parental controls.",
                docs: ["https://internal/ads-spec"],
                tags: ["ads", "targeting", "minors", "behavioral"],
                code_hints: ["if user.age < 18:", "checkParentalConsent()"]
            }
        ];

        document.getElementById('bulk_features').value = JSON.stringify(template, null, 2);
        this.showNotification('Template loaded successfully', 'success');
    }

    validateJSON() {
        const textarea = document.getElementById('bulk_features');
        try {
            const data = JSON.parse(textarea.value);
            if (!Array.isArray(data)) {
                throw new Error('Root element must be an array');
            }
            this.showNotification('JSON is valid', 'success');
        } catch (error) {
            this.showNotification(`JSON validation error: ${error.message}`, 'error');
        }
    }

    switchInputMethod() {
        const selected = document.querySelector('input[name="input-method"]:checked').value;
        
        document.querySelectorAll('.json-input, .csv-input').forEach(el => {
            el.style.display = 'none';
        });
        
        if (selected === 'json' || selected === 'template') {
            document.querySelector('.json-input').style.display = 'block';
        } else if (selected === 'csv') {
            document.querySelector('.csv-input').style.display = 'block';
        }
    }

    handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const csv = e.target.result;
                const features = this.parseCSVToFeatures(csv);
                document.getElementById('bulk_features').value = JSON.stringify(features, null, 2);
                this.showNotification(`Loaded ${features.length} features from CSV`, 'success');
            } catch (error) {
                this.showNotification(`Failed to parse CSV: ${error.message}`, 'error');
            }
        };
        reader.readAsText(file);
    }

    parseCSVToFeatures(csv) {
        const lines = csv.split('\n').filter(line => line.trim());
        if (lines.length < 2) throw new Error('CSV must have headers and at least one data row');
        
        const headers = lines[0].split(',').map(h => h.trim());
        const features = [];
        
        for (let i = 1; i < lines.length; i++) {
            const values = lines[i].split(',').map(v => v.trim());
            const feature = {};
            
            headers.forEach((header, index) => {
                if (values[index]) {
                    if (header === 'docs' || header === 'tags' || header === 'code_hints') {
                        feature[header] = values[index].split(';').map(s => s.trim());
                    } else {
                        feature[header] = values[index];
                    }
                }
            });
            
            if (feature.feature_id && feature.title && feature.description) {
                features.push(feature);
            }
        }
        
        return features;
    }

    // Modal Management
    showSystemHealth() {
        const modal = document.getElementById('system-health-modal');
        const content = document.getElementById('health-modal-content');
        
        if (this.systemHealth) {
            content.innerHTML = `
                <div class="system-health-details">
                    <div class="health-item">
                        <span class="label">Status:</span>
                        <span class="value ${this.systemHealth.ok ? 'text-success' : 'text-danger'}">
                            ${this.systemHealth.ok ? 'Healthy' : 'Error'}
                        </span>
                    </div>
                    <div class="health-item">
                        <span class="label">Rules Hash:</span>
                        <span class="value"><code>${this.systemHealth.rules_hash || 'N/A'}</code></span>
                    </div>
                    <div class="health-item">
                        <span class="label">Vector Store Documents:</span>
                        <span class="value">${this.systemHealth.mem0_docs || 0}</span>
                    </div>
                    <div class="health-item">
                        <span class="label">Policy Version:</span>
                        <span class="value">${this.systemHealth.policy_version || 'N/A'}</span>
                    </div>
                    ${this.systemHealth.error ? `
                        <div class="health-item">
                            <span class="label">Error:</span>
                            <span class="value text-danger">${this.systemHealth.error}</span>
                        </div>
                    ` : ''}
                </div>
            `;
        }
        
        this.showModal(modal);
    }

    showSettings() {
        this.showModal(document.getElementById('settings-modal'));
    }

    showModal(modal) {
        modal.classList.add('show');
    }

    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        modal.classList.remove('show');
    }

    saveSettings() {
        const apiUrl = document.getElementById('api-base-url').value;
        const autoRefresh = document.getElementById('auto-refresh').checked;
        
        // Save to localStorage
        localStorage.setItem('geogov-settings', JSON.stringify({
            apiBase: apiUrl,
            autoRefresh: autoRefresh
        }));
        
        this.apiBase = apiUrl;
        this.showNotification('Settings saved successfully', 'success');
        this.closeModal('settings-modal');
    }

    loadSettings() {
        const saved = localStorage.getItem('geogov-settings');
        if (saved) {
            try {
                const settings = JSON.parse(saved);
                this.apiBase = settings.apiBase || this.apiBase;
                
                // Update UI
                document.getElementById('api-base-url').value = this.apiBase;
                document.getElementById('auto-refresh').checked = settings.autoRefresh || false;
            } catch (error) {
                console.warn('Failed to load settings:', error);
            }
        }
    }

    // UI Helpers
    showLoading(text = 'Loading...') {
        const overlay = document.getElementById('loading-overlay');
        const loadingText = document.getElementById('loading-text');
        
        loadingText.textContent = text;
        overlay.classList.add('show');
    }

    hideLoading() {
        document.getElementById('loading-overlay').classList.remove('show');
    }

    showNotification(message, type = 'info') {
        const container = document.getElementById('notifications');
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" style="background: none; border: none; font-size: 1.2em; cursor: pointer; margin-left: auto;">&times;</button>
            </div>
        `;
        
        container.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    handleKeyboardShortcuts(event) {
        // Ctrl/Cmd + K for quick search
        if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
            event.preventDefault();
            document.getElementById('feature_id').focus();
        }
        
        // Ctrl/Cmd + Enter to run analysis
        if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
            event.preventDefault();
            if (this.currentView === 'single-analysis') {
                this.analyzeFeature();
            } else if (this.currentView === 'bulk-analysis') {
                this.runBulkAnalysis();
            }
        }
    }

    async loadAuditTrail() {
        // Mock audit trail data - in production this would come from the API
        const mockData = {
            totalReceipts: this.analysisResults.length,
            merkleRoot: 'sha256-abcd1234...',
            policyVersion: 'v0.1.0'
        };

        document.getElementById('total-receipts').textContent = mockData.totalReceipts;
        document.getElementById('merkle-root').textContent = mockData.merkleRoot;
        document.getElementById('policy-version').textContent = mockData.policyVersion;

        // Display recent receipts
        const auditTrail = document.getElementById('audit-trail');
        if (this.analysisResults.length > 0) {
            auditTrail.innerHTML = `
                <table>
                    <thead>
                        <tr>
                            <th>Hash</th>
                            <th>Feature ID</th>
                            <th>Decision</th>
                            <th>Timestamp</th>
                            <th>Policy Version</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${this.analysisResults.slice(-20).map(result => `
                            <tr>
                                <td><code>${result.hash || 'N/A'}</code></td>
                                <td>${result.feature_id}</td>
                                <td>
                                    <span class="${result.needs_geo_compliance ? 'text-danger' : 'text-success'}">
                                        ${result.needs_geo_compliance ? 'Required' : 'Not Required'}
                                    </span>
                                </td>
                                <td>${new Date(result.ts).toLocaleString()}</td>
                                <td>${result.policy_version}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        } else {
            auditTrail.innerHTML = '<p>No audit records found</p>';
        }
    }
}

// Initialize the application
const app = new GeoGovApp();

// Expose globally for debugging
window.app = app;

// Additional utility functions for the HTML
function showSystemHealth() {
    app.showSystemHealth();
}

function showSettings() {
    app.showSettings();
}

function closeModal(modalId) {
    app.closeModal(modalId);
}

function saveSettings() {
    app.saveSettings();
}

function loadExampleFeature() {
    app.loadExampleFeature();
}

function loadBulkTemplate() {
    app.loadBulkTemplate();
}

function validateJSON() {
    app.validateJSON();
}

function previewBulkAnalysis() {
    app.showNotification('Bulk analysis preview - feature coming soon', 'info');
}

function analyzeFeature() {
    app.analyzeFeature();
}

function runBulkAnalysis() {
    app.runBulkAnalysis();
}

function refreshCorpus() {
    app.refreshCorpus();
}

function checkCorpusStatus() {
    app.loadCorpusStatus();
}

function downloadEvidence() {
    app.downloadEvidence();
}

function downloadCSV() {
    app.downloadCSV();
}

function downloadAuditTrail() {
    app.showNotification('Audit trail download - feature coming soon', 'info');
}