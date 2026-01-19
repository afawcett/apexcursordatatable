import { LightningElement } from 'lwc';
import loadMoreRecords from '@salesforce/apex/ApexCursorDemoController.loadMoreRecords';
import loadMoreRecordsWithPagination from '@salesforce/apex/ApexCursorDemoController.loadMoreRecordsWithPagination';

export default class ApexCursorDemo extends LightningElement {

    records = [];
    offset = 0;
    hasMore = false;
    totalRecords = 0;
    isLoading = false;
    cursor = null;
    paginationCursor = null;
    usePaginationCursors = true;
    deletedRows = 0;

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
        // Reset all state
        this.records = [];
        this.offset = 0;
        this.cursor = null;
        this.paginationCursor = null;
        this.hasMore = false;
        this.totalRecords = 0;
        this.deletedRows = 0;
        this.error = null;
        // Reload from first page
        this.onLoadMoreRecords();
    }

    async onLoadMoreRecords() {
        if(this.isLoading) 
            return;
        this.isLoading = true;
        try {
            let result;
            if (this.usePaginationCursors) {
                // Use pagination cursor method
                result = await loadMoreRecordsWithPagination({
                    paginationCursor: this.paginationCursor,
                    start: this.offset,
                    pageSize: 50
                });
                this.paginationCursor = result.paginationCursor;
                this.deletedRows = result.deletedRows || 0;
            } else {
                // Use standard cursor method
                result = await loadMoreRecords({
                    cursor: this.cursor, 
                    offset: this.offset, 
                    batchSize: 50
                });
                this.cursor = result.cursor;
            }
            
            this.records = [...this.records, ...result.records];
            this.offset = result.offset;
            this.hasMore = result.hasMore;
            this.totalRecords = result.totalRecords;            
        } catch (error) {
            console.error('Error fetching next records:', error);
            this.error = error.body?.message || error.message || 'Unknown error occurred';
            this.hasMore = false;
        } finally {
            this.isLoading = false;
        }
    }

    get cursorTypeLabel() {
        return this.usePaginationCursors ? 'Pagination Cursor' : 'Standard Cursor';
    }

    columns = [
        {
            label: 'Account Name',
            fieldName: 'Name',
            type: 'text',
            initialWidth: 300
        },
        {
            label: 'Industry',
            fieldName: 'Industry',
            type: 'text',
            initialWidth: 150
        },
        {
            label: 'Type',
            fieldName: 'Type',
            type: 'text',
            initialWidth: 120
        },
        {
            label: 'Billing City',
            fieldName: 'BillingCity',
            type: 'text',
            initialWidth: 150
        },
        {
            label: 'Phone',
            fieldName: 'Phone',
            type: 'phone',
            initialWidth: 140
        }
    ];
}