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
            result.offset = offset + batchSize;
            result.totalRecords = cursor.getNumRecords();
            result.hasMore = result.offset < result.totalRecords;
            return result;
        } catch (Exception e) {
            Cache.Session.remove('allaccounts');
            throw new AuraHandledException('Error loading records: ' + e.getMessage());
        }
    }
    
    public class LoadMoreRecordsResult {
        @AuraEnabled public Database.Cursor cursor;
        @AuraEnabled public List<Account> records;
        @AuraEnabled public Integer offset;
        @AuraEnabled public Boolean hasMore;
        @AuraEnabled public Integer totalRecords;
    }
}