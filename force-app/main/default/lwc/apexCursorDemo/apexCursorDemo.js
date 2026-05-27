import { LightningElement } from 'lwc';
import loadMoreRecords from '@salesforce/apex/ApexCursorDemoController.loadMoreRecords';
import loadMoreRecordsWithPagination from '@salesforce/apex/ApexCursorDemoController.loadMoreRecordsWithPagination';

const PAGE_SIZE = 50;

/**
 * Infinite-scroll datatable demo for standard and pagination Apex cursors.
 * Supports optional session cache, limit reporting, client-only refresh,
 * and clickable account record links.
 */
export default class ApexCursorDemo extends LightningElement {

    records = [];
    offset = 0;
    hasMore = false;
    isLoading = false;
    cursor = null;
    paginationCursor = null;
    cursorType = 'pagination';
    cursorTypeOptions = [
        { label: 'Standard Cursor', value: 'standard' },
        { label: 'Pagination Cursor', value: 'pagination' }
    ];
    /** Tri-state session cache: true, false, or null (auto-detect from Apex session). */
    useSessionCache = null;
    limitsInfo = null;
    debugInfo = null;
    allowInfiniteLoading = false;
    error = null;
    columns = [
        {
            fieldName: 'accountUrl',
            initialWidth: 300,
            label: 'Account Name',
            type: 'url',
            typeAttributes: {
                label: { fieldName: 'Name' },
                target: '_self'
            }
        },
        {
            fieldName: 'Industry',
            initialWidth: 150,
            label: 'Industry',
            type: 'text'
        },
        {
            fieldName: 'Type',
            initialWidth: 120,
            label: 'Type',
            type: 'text'
        },
        {
            fieldName: 'BillingCity',
            initialWidth: 150,
            label: 'Billing City',
            type: 'text'
        },
        {
            fieldName: 'Phone',
            initialWidth: 140,
            label: 'Phone',
            type: 'phone'
        }
    ];

    /** Loads the first page when the component is inserted into the DOM. */
    connectedCallback() {
        this.onLoadMoreRecords();
    }

    /**
     * Switches between standard and pagination cursor modes.
     * Resets paging state and reloads from the first page.
     */
    handleCursorTypeChange(event) {
        const newValue = event.detail.value;
        if (this.cursorType !== newValue) {
            this.cursorType = newValue;
            this.resetAndReload();
        }
    }

    /**
     * Toggles explicit session-cache use.
     * Resets paging state and reloads from the first page.
     */
    handleSessionCacheChange(event) {
        const newValue = event.target.checked;
        if (this.useSessionCache !== newValue) {
            this.useSessionCache = newValue;
            this.resetAndReload();
        }
    }

    /**
     * Resets paging state after a cursor-type or session-cache change,
     * then reloads from the first page.
     */
    resetAndReload() {
        this.resetViewState();
        this.onLoadMoreRecords();
    }

    /** Clears loaded rows and paging state without changing cursor type or cache settings. */
    resetViewState() {
        this.records = [];
        this.offset = 0;
        this.cursor = null;
        this.paginationCursor = null;
        this.hasMore = false;
        this.limitsInfo = null;
        this.debugInfo = null;
        this.allowInfiniteLoading = false;
        this.error = null;
    }

    /**
     * Client-only refresh: reloads the first page with the current
     * cursor type and session-cache settings unchanged.
     */
    handleRefresh() {
        this.resetViewState();
        this.onLoadMoreRecords();
    }

    /**
     * Loads the next page of records.
     * Invoked on init, infinite scroll, and after reset/refresh.
     */
    async onLoadMoreRecords() {
        if (this.isLoading) {
            return;
        }
        this.isLoading = true;
        try {
            const result = await this.fetchNextPage();
            this.applyLoadResult(result);
        } catch (error) {
            this.handleLoadError(error);
        } finally {
            this.isLoading = false;
        }
    }

    /**
     * Calls the Apex loader for the active cursor type.
     * When session cache is on, cursors are omitted so Apex reads from Cache.Session.
     *
     * @returns Promise resolving to the next page load result.
     */
    fetchNextPage() {
        if (this.cursorType === 'pagination') {
            return loadMoreRecordsWithPagination({
                request: {
                    paginationCursor: this.useSessionCache === true ? null : this.paginationCursor,
                    start: this.offset,
                    pageSize: PAGE_SIZE,
                    useSessionCache: this.useSessionCache
                }
            });
        }
        return loadMoreRecords({
            request: {
                cursor: this.useSessionCache === true ? null : this.cursor,
                offset: this.offset,
                batchSize: PAGE_SIZE,
                useSessionCache: this.useSessionCache
            }
        });
    }

    /**
     * Merges a page of Apex results into component state.
     *
     * @param result Page payload from loadMoreRecords or loadMoreRecordsWithPagination.
     */
    applyLoadResult(result) {
        if (result.usingSessionCache) {
            this.useSessionCache = true;
        }
        if (this.cursorType === 'pagination') {
            // LWC-held cursor is unused while session cache is active.
            if (this.useSessionCache !== true) {
                this.paginationCursor = result.paginationCursor;
            }
        } else if (this.useSessionCache !== true) {
            this.cursor = result.cursor;
        }
        const pageRecords = result.records ?? [];
        this.records = [...this.records, ...this.withAccountUrls(pageRecords)];
        this.offset = result.offset;
        this.hasMore = result.hasMore;
        this.limitsInfo = result.limitsInfo;
        this.debugInfo = this.buildDebugInfo(result);
        this.updateInfiniteLoadingFlag();
    }

    /**
     * Builds the debug panel snapshot from the latest Apex response.
     *
     * @param result Page payload from loadMoreRecords or loadMoreRecordsWithPagination.
     * @returns Debug fields for display after a successful load.
     */
    buildDebugInfo(result) {
        return {
            loadedRecords: this.records.length,
            totalRecords: result.totalRecords,
            hasMore: result.hasMore,
            cursorTypeLabel: this.cursorType === 'pagination' ? 'Pagination Cursor' : 'Standard Cursor',
            usingSessionCache: result.usingSessionCache,
            deletedRows: result.deletedRows || 0,
            isPagination: this.cursorType === 'pagination'
        };
    }

    /**
     * Defers enabling infinite scroll until after the first page paints.
     * Prevents lightning-datatable from firing a duplicate onloadmore on init.
     */
    updateInfiniteLoadingFlag() {
        this.allowInfiniteLoading = false;
        if (this.hasMore && this.records.length > 0) {
            requestAnimationFrame(() => {
                this.allowInfiniteLoading = this.hasMore;
            });
        }
    }

    /**
     * Adds record-page URLs for the datatable name column.
     *
     * @param records Account rows returned from Apex.
     * @returns Rows with an accountUrl field for url-type columns.
     */
    withAccountUrls(records) {
        return records.map((record) => ({
            ...record,
            accountUrl: `/lightning/r/Account/${record.Id}/view`
        }));
    }

    /** Stops further paging and surfaces the Apex error to the template. */
    handleLoadError(error) {
        this.error = error.body?.message || error.message || 'Unknown error occurred';
        this.hasMore = false;
        this.allowInfiniteLoading = false;
    }
}
