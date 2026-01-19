public with sharing class ApexCursorDemoController {
    
    @AuraEnabled(cacheable=false)
    public static LoadMoreRecordsResult loadMoreRecords(Database.Cursor cursor, Integer offset, Integer batchSize) {
        try {
            if(cursor == null) {
                cursor = Database.getCursor('SELECT Id, Name, Industry, Type, BillingCity, Phone FROM Account WHERE Name LIKE \'TEST%\' ORDER BY Name', AccessLevel.USER_MODE);
            }            
            LoadMoreRecordsResult result = new LoadMoreRecordsResult();
            result.cursor = cursor;
            result.records = cursor.fetch(offset, batchSize);
            result.offset = offset + result.records.size(); // Update offset based on actual number of records fetched
            result.totalRecords = cursor.getNumRecords();
            result.hasMore = result.offset < result.totalRecords;
            return result;
        } catch (Exception e) {
            throw new AuraHandledException('Error loading records: ' + e.getMessage());
        }
    }
    
    @AuraEnabled(cacheable=false)
    public static LoadMoreRecordsResult loadMoreRecordsWithPagination(Database.PaginationCursor paginationCursor, Integer start, Integer pageSize) {
        try {
            if(paginationCursor == null) {
                paginationCursor = Database.getPaginationCursor('SELECT Id, Name, Industry, Type, BillingCity, Phone FROM Account WHERE Name LIKE \'TEST%\' ORDER BY Name', AccessLevel.USER_MODE);
            }
                        
            LoadMoreRecordsResult result = new LoadMoreRecordsResult();
            Database.CursorFetchResult fetchResult = paginationCursor.fetchPage(start, pageSize);
            result.paginationCursor = paginationCursor;
            result.records = fetchResult.getRecords();
            result.offset = fetchResult.getNextIndex();
            result.totalRecords = paginationCursor.getNumRecords();
            result.hasMore = result.offset < result.totalRecords;
            result.deletedRows = fetchResult.getNumDeletedRecords();
            return result;
        } catch (Exception e) {
            throw new AuraHandledException('Error loading records with pagination: ' + e.getMessage());
        }
    }
    
    public class LoadMoreRecordsResult {
        @AuraEnabled public Database.Cursor cursor;
        @AuraEnabled public Database.PaginationCursor paginationCursor;
        @AuraEnabled public List<Account> records;
        @AuraEnabled public Integer offset;
        @AuraEnabled public Boolean hasMore;
        @AuraEnabled public Integer totalRecords;
        @AuraEnabled public Integer deletedRows;
    }
}