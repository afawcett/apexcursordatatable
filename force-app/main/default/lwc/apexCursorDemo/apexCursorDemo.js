import { LightningElement } from 'lwc';
import loadMoreRecords from '@salesforce/apex/ApexCursorDemoController.loadMoreRecords';
import loadMoreRecordsWithPagination from '@salesforce/apex/ApexCursorDemoController.loadMoreRecordsWithPagination';

const COLUMNS = [
    {
        fieldName: 'Name',
        initialWidth: 300,
        label: 'Account Name',
        type: 'text'
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
    ],
    INITIAL_DELETED_ROWS = 0,
    INITIAL_OFFSET = 0,
    INITIAL_TOTAL = 0,
    PAGE_SIZE = 50,
    CURSOR_TYPE_OPTIONS = [
        { label: 'Standard Cursor', value: 'standard' },
        { label: 'Pagination Cursor', value: 'pagination' }
    ];

export default class ApexCursorDemo extends LightningElement {

    records = [];
    offset = INITIAL_OFFSET;
    hasMore = false;
    totalRecords = INITIAL_TOTAL;
    isLoading = false;
    cursor = null;
    paginationCursor = null;
    cursorType = 'pagination';
    cursorTypeOptions = CURSOR_TYPE_OPTIONS;
    useSessionCache = null;
    deletedRows = INITIAL_DELETED_ROWS;
    usingSessionCache = false;
    limitsInfo = null;
    columns = COLUMNS;

    connectedCallback() {
        this.onLoadMoreRecords();
    }

    handleCursorTypeChange(event) {
        const newValue = event.detail.value;
        if (this.cursorType !== newValue) {
            this.cursorType = newValue;
            this.resetAndReload();
        }
    }

    handleSessionCacheChange(event) {
        const newValue = event.target.checked;
        if (this.useSessionCache !== newValue) {
            this.useSessionCache = newValue;
            this.resetAndReload();
        }
    }

    resetAndReload() {
        this.records = [];
        this.offset = INITIAL_OFFSET;
        this.cursor = null;
        this.paginationCursor = null;
        this.hasMore = false;
        this.totalRecords = INITIAL_TOTAL;
        this.deletedRows = INITIAL_DELETED_ROWS;
        this.usingSessionCache = false;
        this.limitsInfo = null;
        this.error = null;
        this.onLoadMoreRecords();
    }

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

    fetchNextPage() {
        const useSessionCache = this.useSessionCache === true ? true : this.useSessionCache === false ? false : null;
        if (this.usePaginationCursors) {
            return loadMoreRecordsWithPagination({
                pageSize: PAGE_SIZE,
                paginationCursor: this.useSessionCache === true ? null : this.paginationCursor,
                start: this.offset,
                useSessionCache
            });
        }
        return loadMoreRecords({
            batchSize: PAGE_SIZE,
            cursor: this.useSessionCache === true ? null : this.cursor,
            offset: this.offset,
            useSessionCache
        });
    }

    applyLoadResult(result) {
        this.usingSessionCache = result.usingSessionCache;
        if (result.usingSessionCache) {
            this.useSessionCache = true;
        }
        if (this.usePaginationCursors) {
            if (this.useSessionCache !== true) {
                this.paginationCursor = result.paginationCursor;
            }
            this.deletedRows = result.deletedRows || INITIAL_DELETED_ROWS;
        } else if (this.useSessionCache !== true) {
            this.cursor = result.cursor;
        }
        this.records = [...this.records, ...result.records];
        this.offset = result.offset;
        this.hasMore = result.hasMore;
        this.totalRecords = result.totalRecords;
        this.limitsInfo = result.limitsInfo;
    }

    formatLimit(used, limit) {
        if (used === undefined || used === null || limit === undefined || limit === null) {
            return '—';
        }
        return `${used}/${limit}`;
    }

    handleLoadError(error) {
        this.error = error.body?.message || error.message || 'Unknown error occurred';
        this.hasMore = false;
    }

    get cursorTypeLabel() {
        if (this.usePaginationCursors) {
            return 'Pagination Cursor';
        }
        return 'Standard Cursor';
    }

    get usePaginationCursors() {
        return this.cursorType === 'pagination';
    }

    get standardCursorsLabel() {
        return this.formatLimit(this.limitsInfo?.apexCursors, this.limitsInfo?.limitApexCursors);
    }

    get standardCursorRowsLabel() {
        return this.formatLimit(this.limitsInfo?.apexCursorRows, this.limitsInfo?.limitApexCursorRows);
    }

    get paginationCursorsLabel() {
        return this.formatLimit(this.limitsInfo?.apexPaginationCursors, this.limitsInfo?.limitApexPaginationCursors);
    }

    get paginationCursorRowsLabel() {
        return this.formatLimit(this.limitsInfo?.apexPaginationCursorRows, this.limitsInfo?.limitApexPaginationCursorRows);
    }

    get fetchCallsLabel() {
        return this.formatLimit(this.limitsInfo?.fetchCallsOnApexCursor, this.limitsInfo?.limitFetchCallsOnApexCursor);
    }

    get dailyStandardCursorsLabel() {
        return this.formatLimit(this.limitsInfo?.dailyApexCursors, this.limitsInfo?.limitDailyApexCursors);
    }

    get dailyPaginationCursorsLabel() {
        return this.formatLimit(this.limitsInfo?.dailyApexPaginationCursors, this.limitsInfo?.limitDailyApexPaginationCursors);
    }

    get dailyCursorRowsLabel() {
        return this.formatLimit(this.limitsInfo?.dailyApexCursorRows, this.limitsInfo?.limitDailyApexCursorRows);
    }
}
