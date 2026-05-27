import { LightningElement } from 'lwc';
import { loadScript } from 'lightning/platformResourceLoader';
import chartjs from '@salesforce/resourceUrl/chartjs';
import initializeSeries from '@salesforce/apex/ReportingDrillDownController.initializeSeries';
import refreshSeries from '@salesforce/apex/ReportingDrillDownController.refreshSeries';
import fetchDetailRange from '@salesforce/apex/ReportingDrillDownController.fetchDetailRange';

const PRODUCT_OPTIONS = [
    { label: 'RAM', value: 'RAM' },
    { label: 'CPU', value: 'CPU' }
];

const MS_PER_DAY = 86400000;

/**
 * Reporting drill-down: monthly chart (cursor mid-month fetches) + brush + daily detail.
 */
export default class ReportingDrillDown extends LightningElement {
    product = 'RAM';
    productOptions = PRODUCT_OPTIONS;
    isLoading = false;
    isChartReady = false;
    error = null;

    rangeStart = null;
    rangeEnd = null;
    dailyRowCount = 0;

    detailRows = [];
    detailStatus = '';
    chartStatus = '';
    selectionSummary = '';

    brushLeft = null;
    brushRight = null;
    activeHandle = null;
    isDraggingNew = false;

    chart;
    chartJsLoaded = false;
    chartArea = null;
    resizeObserver;
    /** Monthly points from cursor fetchPage (effectiveDate as UTC Date). */
    monthlyPoints = [];

    columns = [
        { label: 'Effective Date', fieldName: 'effectiveDateLabel', type: 'text' },
        { label: 'Product', fieldName: 'product', type: 'text' },
        { label: 'Value', fieldName: 'value', type: 'currency', typeAttributes: { currencyCode: 'USD' } }
    ];

    get hasBrushSelection() {
        return this.brushLeft != null && this.brushRight != null;
    }

    get brushBounds() {
        const left = Math.min(this.brushLeft, this.brushRight);
        const right = Math.max(this.brushLeft, this.brushRight);
        return { left, right, width: right - left };
    }

    get brushShadeStyle() {
        const { left, width } = this.brushBounds;
        return `left:${left}px;width:${width}px;`;
    }

    /** Handle sits outside the shade; shade border is the selection edge. */
    get brushHandleLeftStyle() {
        return `left:${this.brushBounds.left}px;`;
    }

    get brushHandleRightStyle() {
        return `left:${this.brushBounds.right}px;`;
    }

    connectedCallback() {
        this.loadChartLibrary()
            .then(() => this.loadSeries(false))
            .catch((err) => {
                this.error = this.messageFromError(err);
            });
    }

    disconnectedCallback() {
        if (this.resizeObserver) {
            this.resizeObserver.disconnect();
        }
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }

    async loadChartLibrary() {
        if (this.chartJsLoaded) {
            return;
        }
        await loadScript(this, chartjs + '/chart.umd.min.js');
        this.chartJsLoaded = true;
    }

    async loadSeries(isRefresh) {
        this.isLoading = true;
        this.error = null;
        this.detailRows = [];
        this.clearBrush();
        try {
            const result = isRefresh
                ? await refreshSeries({ product: this.product })
                : await initializeSeries({ product: this.product });
            this.applySeriesResult(result);
        } catch (err) {
            this.error = this.messageFromError(err);
            this.isChartReady = false;
        } finally {
            this.isLoading = false;
        }
    }

    applySeriesResult(result) {
        this.rangeStart = this.parseSalesforceDate(result.rangeStart);
        this.rangeEnd = this.parseSalesforceDate(result.rangeEnd);
        this.dailyRowCount = result.dailyRowCount ?? 0;

        if (!result.monthlyPoints?.length || !this.rangeStart || !this.rangeEnd) {
            this.isChartReady = false;
            this.chartStatus = '';
            this.error = 'No observations found. Run the data import script, then Refresh.';
            return;
        }

        this.chartStatus = `Chart: ${result.monthlyPoints.length} monthly points from ${result.cursorFetchCount ?? 0} cursor fetchPage calls`;
        this.isChartReady = true;
        requestAnimationFrame(() => this.renderChart(result.monthlyPoints));
    }

    renderChart(monthlyPoints) {
        const canvas = this.template.querySelector('canvas.chart-canvas');
        if (!canvas || !window.Chart) {
            return;
        }

        if (this.chart) {
            this.chart.destroy();
        }

        this.monthlyPoints = monthlyPoints.map((p) => ({
            effectiveDate: this.parseSalesforceDate(p.effectiveDate),
            value: p.value,
            dayIndex: p.dayIndex
        }));

        const labels = this.monthlyPoints.map((p) => this.formatMonthLabel(p.effectiveDate));
        const values = this.monthlyPoints.map((p) => p.value);

        this.chart = new window.Chart(canvas, {
            type: 'line',
            data: {
                labels,
                datasets: [
                    {
                        label: `${this.product} monthly price (mid-month, cursor)`,
                        data: values,
                        borderColor: '#0176d3',
                        backgroundColor: 'rgba(1, 118, 211, 0.08)',
                        fill: true,
                        tension: 0.2,
                        pointRadius: 0,
                        pointHitRadius: 8
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { mode: 'index', intersect: false },
                plugins: {
                    legend: { display: true },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => ` $${Number(ctx.parsed.y).toFixed(2)}`
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            autoSkip: false,
                            maxRotation: 90,
                            minRotation: 45,
                            font: { size: 9 }
                        }
                    },
                    y: {
                        title: { display: true, text: 'Unit price (USD)' }
                    }
                },
                animation: false
            }
        });

        this.syncChartArea();
        if (!this.resizeObserver && typeof ResizeObserver !== 'undefined') {
            const shell = this.template.querySelector('.chart-shell');
            this.resizeObserver = new ResizeObserver(() => this.syncChartArea());
            this.resizeObserver.observe(shell);
        }
    }

    syncChartArea() {
        if (!this.chart) {
            return;
        }
        this.chart.update('none');
        const area = this.chart.chartArea;
        if (!area) {
            return;
        }
        const shell = this.template.querySelector('.chart-shell');
        const layer = this.template.querySelector('.brush-layer');
        if (!shell || !layer) {
            return;
        }
        const rect = shell.getBoundingClientRect();
        this.chartArea = {
            left: area.left,
            right: area.right,
            top: area.top,
            bottom: area.bottom,
            width: area.right - area.left
        };
        layer.style.left = `${area.left}px`;
        layer.style.top = `${area.top}px`;
        layer.style.width = `${this.chartArea.width}px`;
        layer.style.height = `${area.bottom - area.top}px`;
    }

    handleProductChange(event) {
        const value = event.detail.value;
        if (value && value !== this.product) {
            this.product = value;
            this.loadSeries(false);
        }
    }

    handleRefresh() {
        this.loadSeries(true);
    }

    handleBrushMouseDown(event) {
        if (event.target.dataset.handle) {
            return;
        }
        const x = this.localX(event);
        if (x == null) {
            return;
        }
        this.isDraggingNew = true;
        this.brushLeft = x;
        this.brushRight = x;
        this.activeHandle = null;
    }

    handleHandleMouseDown(event) {
        event.stopPropagation();
        this.activeHandle = event.target.dataset.handle;
        this.isDraggingNew = false;
    }

    handleBrushMouseMove(event) {
        const x = this.localX(event);
        if (x == null) {
            return;
        }
        if (this.isDraggingNew) {
            this.brushRight = x;
            return;
        }
        if (this.activeHandle === 'left') {
            this.brushLeft = x;
        } else if (this.activeHandle === 'right') {
            this.brushRight = x;
        }
    }

    handleBrushMouseUp() {
        if (this.isDraggingNew || this.activeHandle) {
            this.isDraggingNew = false;
            this.activeHandle = null;
            this.finalizeBrushSelection();
        }
    }

    handleBrushMouseLeave() {
        if (this.isDraggingNew) {
            this.isDraggingNew = false;
            this.finalizeBrushSelection();
        }
    }

    async finalizeBrushSelection() {
        if (this.brushLeft == null || this.brushRight == null || !this.chartArea?.width) {
            return;
        }

        const { left: leftPx, right: rightPx } = this.brushBounds;
        if (rightPx - leftPx < 4) {
            this.clearBrush();
            return;
        }

        let startIndex = this.pixelToDayIndex(leftPx);
        let endIndex = this.pixelToDayIndex(rightPx);
        if (startIndex > endIndex) {
            const swap = startIndex;
            startIndex = endIndex;
            endIndex = swap;
        }

        const startDate = this.addDaysUtc(this.rangeStart, startIndex);
        const endDate = this.addDaysUtc(this.rangeStart, endIndex);

        this.brushLeft = this.dayIndexToPixel(startIndex);
        this.brushRight = this.dayIndexToPixel(endIndex);

        this.isLoading = true;
        this.error = null;
        try {
            const detail = await fetchDetailRange({
                product: this.product,
                startIndex,
                endIndex
            });
            this.detailRows = (detail.records ?? []).map((row, idx) => ({
                rowKey: `${row.product}-${row.effectiveDate}-${idx}`,
                effectiveDateLabel: this.formatDateLabel(row.effectiveDate),
                product: row.product,
                value: row.value
            }));
            this.selectionSummary = `Selected ${this.formatDateLabel(startDate)} → ${this.formatDateLabel(endDate)} (cursor indexes ${startIndex}–${endIndex})`;
            const deleted = detail.deletedRows ?? 0;
            this.detailStatus = `Showing ${this.detailRows.length} daily observation(s) from pagination cursor fetchPage(${detail.startIndex}, ${this.detailRows.length}).`;
            if (deleted > 0) {
                this.detailStatus += ` (${deleted} deleted row(s) skipped by cursor.)`;
            }
        } catch (err) {
            this.error = this.messageFromError(err);
            this.detailRows = [];
        } finally {
            this.isLoading = false;
        }
    }

    clearBrush() {
        this.brushLeft = null;
        this.brushRight = null;
        this.selectionSummary = '';
    }

    localX(event) {
        const layer = this.template.querySelector('.brush-layer');
        if (!layer || !this.chartArea) {
            return null;
        }
        const rect = layer.getBoundingClientRect();
        let x = event.clientX - rect.left;
        x = Math.max(0, Math.min(this.chartArea.width, x));
        return x;
    }

    /**
     * Maps brush-layer X to a calendar date using the chart's category x-scale
     * (monthly points are evenly spaced on the axis, not linear in calendar time).
     */
    pixelToDate(px) {
        const xScale = this.chart?.scales?.x;
        if (!xScale || !this.chartArea || !this.monthlyPoints.length) {
            return null;
        }
        const canvasX = this.chartArea.left + px;
        const index = xScale.getValueForPixel(canvasX);
        if (index == null || Number.isNaN(index)) {
            return null;
        }
        return this.interpolateChartDate(index);
    }

    /** Maps a cursor day index to brush-layer X via the chart x-scale. */
    dayIndexToPixel(dayIndex) {
        return this.dateToPixel(this.addDaysUtc(this.rangeStart, dayIndex));
    }

    /** Maps brush-layer X to inclusive cursor day index. */
    pixelToDayIndex(px) {
        const date = this.pixelToDate(px);
        if (!date) {
            return 0;
        }
        return this.clampIndex(this.dayIndexFromDate(date));
    }

    /** Maps a calendar date back to brush-layer X via the chart x-scale. */
    dateToPixel(date) {
        const xScale = this.chart?.scales?.x;
        if (!xScale || !this.chartArea || !this.monthlyPoints.length) {
            return 0;
        }
        const index = this.dateToChartIndex(date);
        const canvasX = xScale.getPixelForValue(index);
        return canvasX - this.chartArea.left;
    }

    interpolateChartDate(index) {
        const points = this.monthlyPoints;
        const maxIdx = points.length - 1;
        const clamped = Math.max(0, Math.min(maxIdx, index));
        const lo = Math.floor(clamped);
        const hi = Math.ceil(clamped);
        if (lo === hi) {
            return this.snapToUtcDay(points[lo].effectiveDate);
        }
        const d0 = points[lo].effectiveDate.getTime();
        const d1 = points[hi].effectiveDate.getTime();
        const ms = d0 + (clamped - lo) * (d1 - d0);
        return this.snapToUtcDay(new Date(ms));
    }

    dateToChartIndex(date) {
        const points = this.monthlyPoints;
        if (!points.length) {
            return 0;
        }
        const ms = date.getTime();
        if (ms <= points[0].effectiveDate.getTime()) {
            return 0;
        }
        const last = points[points.length - 1].effectiveDate.getTime();
        if (ms >= last) {
            return points.length - 1;
        }
        for (let i = 0; i < points.length - 1; i++) {
            const d0 = points[i].effectiveDate.getTime();
            const d1 = points[i + 1].effectiveDate.getTime();
            if (ms >= d0 && ms <= d1) {
                return d1 === d0 ? i : i + (ms - d0) / (d1 - d0);
            }
        }
        return points.length - 1;
    }

    formatMonthLabel(value) {
        const d = this.parseSalesforceDate(value);
        if (!d) {
            return '';
        }
        const y = d.getUTCFullYear();
        const m = String(d.getUTCMonth() + 1).padStart(2, '0');
        return `${y}-${m}`;
    }

    clampIndex(index) {
        const max = Math.max(0, (this.dailyRowCount ?? 1) - 1);
        return Math.max(0, Math.min(max, index));
    }

    dayIndexFromDate(date) {
        const diff = date.getTime() - this.rangeStart.getTime();
        return Math.floor(diff / MS_PER_DAY);
    }

    addDaysUtc(date, days) {
        return new Date(date.getTime() + days * MS_PER_DAY);
    }

    snapToUtcDay(date) {
        return new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate()));
    }

    parseSalesforceDate(value) {
        if (!value) {
            return null;
        }
        if (typeof value === 'string') {
            const [y, m, d] = value.split('-').map(Number);
            return new Date(Date.UTC(y, m - 1, d));
        }
        return this.snapToUtcDay(new Date(value));
    }

    formatDateLabel(value) {
        const d = this.parseSalesforceDate(value);
        if (!d) {
            return '';
        }
        return d.toISOString().slice(0, 10);
    }

    messageFromError(err) {
        return err?.body?.message || err?.message || 'Unknown error';
    }
}
