import { LightningElement } from 'lwc';
import loadMoreRecords from '@salesforce/apex/ApexCursorDemoController.loadMoreRecords';

export default class ApexCursorDemo extends LightningElement {

    records = [];
    offset = 0;
    hasMore = false;
    totalRecords = 0;
    isLoading = false;
    cursor = null;

    connectedCallback() {
        this.onLoadMoreRecords();
    }

    async onLoadMoreRecords() {
        if(this.isLoading) 
            return;
        this.isLoading = true;
        try {                
            const result = await loadMoreRecords({
                cursor: this.cursor, 
                offset: this.offset, 
                batchSize: 50
            });
            this.records = [...this.records, ...result.records];
            this.cursor = result.cursor;
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