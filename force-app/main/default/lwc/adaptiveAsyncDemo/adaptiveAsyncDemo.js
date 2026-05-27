import { LightningElement } from 'lwc';
import { loadScript } from 'lightning/platformResourceLoader';
import { subscribe, unsubscribe, onError } from 'lightning/empApi';
import chartjs from '@salesforce/resourceUrl/chartjs';
import startRun from '@salesforce/apex/AdaptiveAsyncController.startRun';
import getDemoOrderCount from '@salesforce/apex/AdaptiveAsyncController.getDemoOrderCount';

const CHANNEL = '/event/AdaptiveAsyncChunk__e';

/**
 * Adaptive async demo: empApi chunk events drive progress bar, bar chart, and datatable.
 */
export default class AdaptiveAsyncDemo extends LightningElement {
    demoOrderCount = 0;
    runId = null;
    totalOrders = 0;
    maxCalloutsPerChunk = 100;
    processedTotal = 0;
    chunkEvents = [];
    isRunning = false;
    isChartReady = false;
    error = null;
    chartStatus = '';

    chart;
    chartJsLoaded = false;
    subscription = null;

    columns = [
        { label: 'Seq', fieldName: 'sequence', type: 'number', initialWidth: 70 },
        { label: 'Planned', fieldName: 'planned', type: 'number', initialWidth: 90 },
        { label: 'Processed', fieldName: 'actual', type: 'number', initialWidth: 100 },
        { label: 'Callouts', fieldName: 'callouts', type: 'number', initialWidth: 90 },
        { label: 'Success', fieldName: 'successLabel', type: 'text', initialWidth: 90 },
        { label: 'Job Id', fieldName: 'jobId', type: 'text' },
        { label: 'Error', fieldName: 'errorMessage', type: 'text', wrapText: true }
    ];

    get demoOrderLabel() {
        return `${this.demoOrderCount} demo order(s) · max ${this.maxCalloutsPerChunk} HTTP callouts/chunk`;
    }

    get progressPercent() {
        if (!this.totalOrders) {
            return 0;
        }
        return Math.min(100, Math.round((this.processedTotal / this.totalOrders) * 100));
    }

    get progressLabel() {
        return `${this.processedTotal} / ${this.totalOrders} orders (${this.progressPercent}%) · chunk ${this.chunkEvents.length}`;
    }

    get progressVariant() {
        return this.progressPercent >= 100 ? 'success' : 'base';
    }

    get hasEvents() {
        return this.eventRows.length > 0;
    }

    get eventRows() {
        return this.chunkEvents.map((evt) => ({
            rowKey: `${evt.sequence}-${evt.jobId}`,
            sequence: evt.sequence,
            planned: evt.planned,
            actual: evt.actual,
            callouts: evt.callouts,
            successLabel: evt.success ? 'Yes' : 'No',
            jobId: evt.jobId,
            errorMessage: evt.errorMessage || ''
        }));
    }

    get tableStatus() {
        return `Chunk telemetry (${this.eventRows.length} events)`;
    }

    connectedCallback() {
        this.registerEmpErrorListener();
        this.loadChartLibrary()
            .then(() =>
                Promise.all([this.refreshDemoOrderCount(), this.ensureSubscription()])
            )
            .catch((err) => {
                this.error = this.messageFromError(err);
            });
    }

    disconnectedCallback() {
        this.teardownSubscription();
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }

    registerEmpErrorListener() {
        onError(() => {
            this.error = 'Platform event subscription error. Check permissions for AdaptiveAsyncChunk__e.';
        });
    }

    async loadChartLibrary() {
        if (this.chartJsLoaded) {
            return;
        }
        await loadScript(this, chartjs + '/chart.umd.min.js');
        this.chartJsLoaded = true;
    }

    async refreshDemoOrderCount() {
        try {
            this.demoOrderCount = await getDemoOrderCount();
        } catch (err) {
            this.error = this.messageFromError(err);
        }
    }

    async handleStart() {
        this.error = null;
        this.isRunning = true;
        this.runId = null;
        this.totalOrders = 0;
        this.processedTotal = 0;
        this.chunkEvents = [];
        this.isChartReady = false;
        this.chartStatus = '';
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }

        try {
            const info = await startRun();
            this.runId = info.runId;
            this.totalOrders = info.totalOrders;
            this.maxCalloutsPerChunk = info.maxCalloutsPerChunk ?? 100;
            this.isChartReady = true;
            requestAnimationFrame(() => this.renderChart());
        } catch (err) {
            this.error = this.messageFromError(err);
            this.isRunning = false;
        }
    }

    async ensureSubscription() {
        if (this.subscription) {
            return;
        }
        this.subscription = await subscribe(CHANNEL, -1, (message) => {
            this.handleChunkEvent(message);
        });
    }

    handleChunkEvent(message) {
        const payload = message?.data?.payload;
        if (!payload || payload.Run_Id__c !== this.runId) {
            return;
        }

        if (payload.Actual_Processed__c > 0) {
            const evt = {
                sequence: payload.Sequence__c,
                planned: payload.Planned_Chunk_Size__c,
                actual: payload.Actual_Processed__c,
                callouts: payload.Predicted_Callouts__c,
                success: payload.Success__c === true,
                jobId: payload.Job_Id__c,
                errorMessage: payload.Error_Message__c
            };

            this.chunkEvents = [...this.chunkEvents, evt];
            this.processedTotal += evt.actual || 0;
            this.renderChart();
            this.chartStatus = `Chunk ${evt.sequence}: ${evt.actual} orders · ${evt.callouts} predicted callouts`;
        }

        if (payload.Run_Complete__c === true) {
            this.isRunning = false;
            const suffix = payload.Error_Message__c ? ` — ${payload.Error_Message__c}` : '';
            this.chartStatus = `Run complete after ${this.chunkEvents.length} chunk(s).${suffix}`;
            this.refreshDemoOrderCount();
        }
    }

    renderChart() {
        const canvas = this.template.querySelector('canvas.chart-canvas');
        if (!canvas || !window.Chart) {
            return;
        }

        const labels = this.chunkEvents.map((e) => `#${e.sequence}`);
        const values = this.chunkEvents.map((e) => e.actual);
        const colors = this.chunkEvents.map((e) => this.colorForCallouts(e.callouts));

        if (this.chart) {
            this.chart.data.labels = labels;
            this.chart.data.datasets[0].data = values;
            this.chart.data.datasets[0].backgroundColor = colors;
            this.chart.update();
            return;
        }

        this.chart = new window.Chart(canvas, {
            type: 'bar',
            data: {
                labels,
                datasets: [
                    {
                        label: 'Orders processed per chunk',
                        data: values,
                        backgroundColor: colors,
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            afterLabel: (ctx) => {
                                const evt = this.chunkEvents[ctx.dataIndex];
                                if (!evt) {
                                    return '';
                                }
                                return [
                                    `Planned: ${evt.planned}`,
                                    `Callouts: ${evt.callouts}`,
                                    `Job: ${evt.jobId}`
                                ];
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: { display: true, text: 'Chunk sequence' }
                    },
                    y: {
                        beginAtZero: true,
                        title: { display: true, text: 'Orders processed' }
                    }
                },
                animation: { duration: 200 }
            }
        });
    }

    colorForCallouts(callouts) {
        if (callouts >= 90) {
            return '#ea001e';
        }
        if (callouts >= 50) {
            return '#fe9339';
        }
        return '#2e844a';
    }

    teardownSubscription() {
        if (!this.subscription) {
            return;
        }
        const sub = this.subscription;
        this.subscription = null;
        unsubscribe(sub, () => {});
    }

    messageFromError(err) {
        if (Array.isArray(err?.body)) {
            return err.body.map((e) => e.message).join(', ');
        }
        return err?.body?.message || err?.message || String(err);
    }
}
