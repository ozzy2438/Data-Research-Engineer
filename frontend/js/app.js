// Data Research Engineer - Frontend Application
console.log('Data Research Engineer application loaded');

class ResearchApp {
    constructor() {
        this.apiBase = 'http://localhost:8000';
        this.currentJobId = null;
        this.initializeApp();
    }

    initializeApp() {
        console.log('Initializing Research App...');
        
        // DOM elements
        this.researchForm = document.getElementById('research-form');
        this.progressSection = document.getElementById('research-progress');
        this.progressFill = document.getElementById('progress-fill');
        this.progressText = document.getElementById('progress-text');
        this.foundPdfs = document.getElementById('found-pdfs');
        this.resultsSection = document.getElementById('results-section');
        this.welcomeFeatures = document.getElementById('welcome-features');
        this.tablesContainer = document.getElementById('tables-container');
        this.resultsStats = document.getElementById('results-stats');
        this.researchSummary = document.getElementById('research-summary');
        
        // Manual upload elements
        this.manualPdfInput = document.getElementById('manual-pdf');
        this.uploadBtn = document.getElementById('upload-manual');
        
        this.bindEvents();
    }

    bindEvents() {
        // Research form submission
        this.researchForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.startAutomatedResearch();
        });

        // Manual PDF upload
        this.manualPdfInput.addEventListener('change', () => {
            this.uploadBtn.disabled = !this.manualPdfInput.files.length;
        });

        this.uploadBtn.addEventListener('click', () => {
            this.processManualPdf();
        });

        // Feature card interactions
        document.querySelectorAll('.feature-card').forEach(card => {
            card.addEventListener('click', () => {
                console.log('Feature card clicked:', card.querySelector('h3').textContent);
            });
        });
    }

    async startAutomatedResearch() {
        const topic = document.getElementById('research-topic').value;
        const maxPdfs = parseInt(document.getElementById('pdf-count').value);
        
        if (!topic.trim()) {
            alert('Please enter a research topic');
            return;
        }

        try {
            // Start research
            this.showProgress();
            this.updateProgress(5, 'Starting research...');
            
            const response = await fetch(`${this.apiBase}/research/start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    topic: topic,
                    max_pdfs: maxPdfs
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            this.currentJobId = result.job_id;
            
            // Track progress
            this.trackResearchProgress();
            
        } catch (error) {
            console.error('Research failed:', error);
            this.updateProgress(0, `Error: ${error.message}`);
            this.hideProgressAfterDelay();
        }
    }

    async trackResearchProgress() {
        if (!this.currentJobId) return;

        try {
            const response = await fetch(`${this.apiBase}/research/status/${this.currentJobId}`);
            const status = await response.json();

            this.updateProgress(status.progress, status.message);
            
            if (status.found_pdfs && status.found_pdfs.length > 0) {
                this.displayFoundPdfs(status.found_pdfs);
            }

            if (status.status === 'completed') {
                this.displayResults(status.results);
            } else if (status.status === 'failed') {
                this.updateProgress(0, `Research failed: ${status.error}`);
                this.hideProgressAfterDelay();
            } else {
                // Continue tracking
                setTimeout(() => this.trackResearchProgress(), 2000);
            }

        } catch (error) {
            console.error('Progress tracking failed:', error);
            this.updateProgress(0, `Tracking error: ${error.message}`);
            this.hideProgressAfterDelay();
        }
    }

    async processManualPdf() {
        const file = this.manualPdfInput.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('pdf_file', file);

        try {
            this.showProgress();
            this.updateProgress(10, 'Uploading PDF...');

            const response = await fetch(`${this.apiBase}/pdf/upload`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Upload failed: ${response.status}`);
            }

            const result = await response.json();
            this.currentJobId = result.job_id;
            
            this.updateProgress(30, 'Processing PDF...');
            this.trackPdfProcessing();

        } catch (error) {
            console.error('Manual upload failed:', error);
            this.updateProgress(0, `Upload error: ${error.message}`);
            this.hideProgressAfterDelay();
        }
    }

    async trackPdfProcessing() {
        if (!this.currentJobId) return;

        try {
            const response = await fetch(`${this.apiBase}/pdf/status/${this.currentJobId}`);
            const status = await response.json();

            this.updateProgress(status.progress, status.message);

            if (status.status === 'completed') {
                this.displayResults({
                    tables: status.tables,
                    processing_time: status.processing_time,
                    table_count: status.table_count
                });
            } else if (status.status === 'failed') {
                this.updateProgress(0, `Processing failed: ${status.error}`);
                this.hideProgressAfterDelay();
            } else {
                setTimeout(() => this.trackPdfProcessing(), 1000);
            }

        } catch (error) {
            console.error('Processing tracking failed:', error);
            this.updateProgress(0, `Tracking error: ${error.message}`);
            this.hideProgressAfterDelay();
        }
    }

    showProgress() {
        this.progressSection.style.display = 'block';
        this.disableForm(true);
    }

    hideProgress() {
        this.progressSection.style.display = 'none';
        this.disableForm(false);
    }

    hideProgressAfterDelay() {
        setTimeout(() => this.hideProgress(), 3000);
    }

    updateProgress(percentage, message) {
        this.progressFill.style.width = `${percentage}%`;
        this.progressText.textContent = message;
    }

    displayFoundPdfs(pdfs) {
        const pdfList = pdfs.map(pdf => `📄 ${pdf.title || pdf.url}`).join('<br>');
        this.foundPdfs.innerHTML = `<strong>Found PDFs:</strong><br>${pdfList}`;
    }

    displayResults(results) {
        this.hideProgress();
        this.welcomeFeatures.style.display = 'none';
        this.resultsSection.style.display = 'block';

        // Update stats
        const stats = `${results.table_count || results.tables?.length || 0} tables extracted`;
        this.resultsStats.textContent = stats;

        // Update summary
        if (results.processing_time) {
            this.researchSummary.innerHTML = `
                <h3>Processing Summary</h3>
                <p>Successfully processed PDF(s) in ${results.processing_time.toFixed(2)} seconds.</p>
                <p>Extracted ${results.table_count || 0} tables with automated analysis.</p>
            `;
        }

        // Display tables
        this.displayTables(results.tables || []);
    }

    displayTables(tables) {
        this.tablesContainer.innerHTML = '';

        if (!tables.length) {
            this.tablesContainer.innerHTML = `
                <div class="table-card">
                    <div class="table-content">
                        <p>No tables were found in the processed PDF(s).</p>
                    </div>
                </div>
            `;
            return;
        }

        tables.forEach((table, index) => {
            const tableCard = this.createTableCard(table, index);
            this.tablesContainer.appendChild(tableCard);
        });
    }

    createTableCard(table, index) {
        const card = document.createElement('div');
        card.className = 'table-card';

        const qualityColor = this.getQualityColor(table.quality_score);
        
        card.innerHTML = `
            <div class="table-header">
                <h3>Table ${index + 1}: ${table.name || 'Untitled'}</h3>
                <div class="table-meta">
                    <span>📊 ${table.row_count} rows × ${table.col_count} columns</span>
                    <span>📂 ${table.category || 'General Data'}</span>
                    <span style="color: ${qualityColor}">⭐ Quality: ${table.quality_score || 'N/A'}</span>
                </div>
            </div>
            <div class="table-content">
                ${this.createTableHTML(table)}
                ${table.preview_only ? '<p><em>Showing first 100 rows only</em></p>' : ''}
            </div>
        `;

        return card;
    }

    createTableHTML(table) {
        if (!table.data || !table.data.length) {
            return '<p>No data available for this table.</p>';
        }

        const headers = table.columns || Object.keys(table.data[0]);
        const rows = table.data.slice(0, 50); // Show max 50 rows in preview

        return `
            <table class="data-table">
                <thead>
                    <tr>
                        ${headers.map(header => `<th>${header}</th>`).join('')}
                    </tr>
                </thead>
                <tbody>
                    ${rows.map(row => `
                        <tr>
                            ${headers.map(header => `<td>${row[header] || ''}</td>`).join('')}
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }

    getQualityColor(score) {
        if (!score) return '#666';
        if (score >= 0.8) return '#28a745';
        if (score >= 0.6) return '#ffc107';
        return '#dc3545';
    }

    disableForm(disabled) {
        const button = document.getElementById('start-research');
        const input = document.getElementById('research-topic');
        const select = document.getElementById('pdf-count');
        
        button.disabled = disabled;
        input.disabled = disabled;
        select.disabled = disabled;
        
        if (disabled) {
            button.querySelector('.btn-text').style.display = 'none';
            button.querySelector('.btn-loader').style.display = 'inline';
        } else {
            button.querySelector('.btn-text').style.display = 'inline';
            button.querySelector('.btn-loader').style.display = 'none';
        }
    }
}

// Initialize the application when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing Research App...');
    new ResearchApp();
}); 