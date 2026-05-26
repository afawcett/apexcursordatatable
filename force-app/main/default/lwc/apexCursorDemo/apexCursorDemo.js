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
    PAGE_SIZE = 50;

export default class ApexCursorDemo extends LightningElement {

    records = [];
    offset = INITIAL_OFFSET;
    hasMore = false;
    totalRecords = INITIAL_TOTAL;
    isLoading = false;
    cursor = null;
    paginationCursor = null;
    usePaginationCursors = true;
    deletedRows = INITIAL_DELETED_ROWS;
    columns = COLUMNS;

    connectedCallback() {
        this.onLoadMoreRecords();
    }

    handlePaginationModeChange(event) {
        const newValue = event.target.checked;
        if (this.usePaginationCursors !== newValue) {
            this.usePaginationCursors = newValue;
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
        if (this.usePaginationCursors) {
            return loadMoreRecordsWithPagination({
                pageSize: PAGE_SIZE,
                paginationCursor: this.paginationCursor,
                start: this.offset
            });
        }
        return loadMoreRecords({
            batchSize: PAGE_SIZE,
            cursor: this.cursor,
            offset: this.offset
        });
    }

    applyLoadResult(result) {
        if (this.usePaginationCursors) {
            this.paginationCursor = result.paginationCursor;
            this.deletedRows = result.deletedRows || INITIAL_DELETED_ROWS;
        } else {
            this.cursor = result.cursor;
        }
        this.records = [...this.records, ...result.records];
        this.offset = result.offset;
        this.hasMore = result.hasMore;
        this.totalRecords = result.totalRecords;
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
}
