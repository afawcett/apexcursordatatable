public with sharing class ApexCursorDemoController {
    
    @AuraEnabled(cacheable=false)
    public static LoadMoreRecordsResult loadMoreRecords(Integer offset, Integer batchSize) {
        try {
            Database.Cursor cursor = (Database.Cursor) Cache.Session.get('allaccounts');
            if(cursor == null) {
                cursor = Database.getCursor('SELECT Id, Name, Industry, Type, BillingCity, Phone FROM Account WHERE Name LIKE \'TEST%\' ORDER BY Name', AccessLevel.USER_MODE);
                Cache.Session.put('allaccounts', cursor);
            }            
            LoadMoreRecordsResult result = new LoadMoreRecordsResult();
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
        @AuraEnabled public List<Account> records;
        @AuraEnabled public Integer offset;
        @AuraEnabled public Boolean hasMore;
        @AuraEnabled public Integer totalRecords;
    }
}