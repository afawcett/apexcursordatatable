public with sharing class ApexCursorDemoController {
    private static final String SESSION_STANDARD_CURSOR_KEY = 'apexCursorDemoStandard';
    private static final String SESSION_PAGINATION_CURSOR_KEY = 'apexCursorDemoPagination';
    private static final String ACCOUNT_SOQL =
        'SELECT Id, Name, Industry, Type, BillingCity, Phone FROM Account WHERE Name LIKE \'TEST%\' ORDER BY Name';

    @AuraEnabled(cacheable=false)
    public static LoadMoreRecordsResult loadMoreRecords(
        Database.Cursor cursor,
        Integer offset,
        Integer batchSize,
        Boolean useSessionCache
    ) {
        try {
            useSessionCache = useSessionCache != null ? useSessionCache : Cache.Session.get(SESSION_STANDARD_CURSOR_KEY) != null;
            Boolean usingSessionCache = false;
            if (useSessionCache == true) {
                cursor = (Database.Cursor) Cache.Session.get(SESSION_STANDARD_CURSOR_KEY);
                if (cursor == null) {
                    cursor = Database.getCursor(ACCOUNT_SOQL, AccessLevel.USER_MODE);
                    Cache.Session.put(SESSION_STANDARD_CURSOR_KEY, cursor);
                }
                usingSessionCache = true;
            } else {
                Cache.Session.remove(SESSION_STANDARD_CURSOR_KEY);
                if (cursor == null) {
                    cursor = Database.getCursor(ACCOUNT_SOQL, AccessLevel.USER_MODE);
                }
            }

            LoadMoreRecordsResult result = new LoadMoreRecordsResult();
            result.cursor = cursor;
            result.records = cursor.fetch(offset, Math.min(batchSize, cursor.getNumRecords() - offset));
            result.offset = offset + result.records.size();
            result.totalRecords = cursor.getNumRecords();
            result.hasMore = result.offset < result.totalRecords;
            result.usingSessionCache = usingSessionCache;
            result.limitsInfo = buildCursorLimitsInfo();
            return result;
        } catch (Exception e) {
            Cache.Session.remove(SESSION_STANDARD_CURSOR_KEY);
            throw new AuraHandledException('Error loading records: ' + e.getMessage());
        }
    }

    @AuraEnabled(cacheable=false)
    public static LoadMoreRecordsResult loadMoreRecordsWithPagination(
        Database.PaginationCursor paginationCursor,
        Integer start,
        Integer pageSize,
        Boolean useSessionCache
    ) {
        try {
            useSessionCache = useSessionCache != null ? useSessionCache : Cache.Session.get(SESSION_PAGINATION_CURSOR_KEY) != null;
            Boolean usingSessionCache = false;
            if (useSessionCache == true) {
                paginationCursor = (Database.PaginationCursor) Cache.Session.get(SESSION_PAGINATION_CURSOR_KEY);
                if (paginationCursor == null) {
                    paginationCursor = Database.getPaginationCursor(ACCOUNT_SOQL, AccessLevel.USER_MODE);
                    Cache.Session.put(SESSION_PAGINATION_CURSOR_KEY, paginationCursor);
                }
                usingSessionCache = true;
            } else {
                Cache.Session.remove(SESSION_PAGINATION_CURSOR_KEY);
                if (paginationCursor == null) {
                    paginationCursor = Database.getPaginationCursor(ACCOUNT_SOQL, AccessLevel.USER_MODE);
                }
            }

            LoadMoreRecordsResult result = new LoadMoreRecordsResult();
            Database.CursorFetchResult fetchResult = paginationCursor.fetchPage(start, Math.min(pageSize, paginationCursor.getNumRecords() - start));
            result.paginationCursor = paginationCursor;
            result.records = fetchResult.getRecords();
            result.offset = fetchResult.getNextIndex();
            result.totalRecords = paginationCursor.getNumRecords();
            result.hasMore = result.offset < result.totalRecords;
            result.deletedRows = fetchResult.getNumDeletedRecords();
            result.usingSessionCache = usingSessionCache;
            result.limitsInfo = buildCursorLimitsInfo();
            return result;
        } catch (Exception e) {
            Cache.Session.remove(SESSION_PAGINATION_CURSOR_KEY);
            throw new AuraHandledException('Error loading records with pagination: ' + e.getMessage());
        }
    }

    private static CursorLimitsInfo buildCursorLimitsInfo() {
        CursorLimitsInfo info = new CursorLimitsInfo();
        info.apexCursors = Limits.getApexCursors();
        info.limitApexCursors = Limits.getLimitApexCursors();
        info.apexCursorRows = Limits.getApexCursorRows();
        info.limitApexCursorRows = Limits.getLimitApexCursorRows();
        info.apexPaginationCursors = Limits.getApexPaginationCursors();
        info.limitApexPaginationCursors = Limits.getLimitApexPaginationCursors();
        info.apexPaginationCursorRows = Limits.getApexPaginationCursorRows();
        info.limitApexPaginationCursorRows = Limits.getLimitApexPaginationCursorRows();
        info.fetchCallsOnApexCursor = Limits.getFetchCallsOnApexCursor();
        info.limitFetchCallsOnApexCursor = Limits.getLimitFetchCallsOnApexCursor();

        Map<String, System.OrgLimit> limitMap = OrgLimits.getMap();
        System.OrgLimit dailyCursorLimit = limitMap.get('DailyApexCursorLimit');
        System.OrgLimit dailyPaginationCursorLimit = limitMap.get('DailyApexPCursorLimit');
        System.OrgLimit dailyCursorRowsLimit = limitMap.get('DailyApexCursorRowsLimit');
        if (dailyCursorLimit != null) {
            info.dailyApexCursors = dailyCursorLimit.getValue();
            info.limitDailyApexCursors = dailyCursorLimit.getLimit();
        }
        if (dailyPaginationCursorLimit != null) {
            info.dailyApexPaginationCursors = dailyPaginationCursorLimit.getValue();
            info.limitDailyApexPaginationCursors = dailyPaginationCursorLimit.getLimit();
        }
        if (dailyCursorRowsLimit != null) {
            info.dailyApexCursorRows = dailyCursorRowsLimit.getValue();
            info.limitDailyApexCursorRows = dailyCursorRowsLimit.getLimit();
        }
        return info;
    }

    public class LoadMoreRecordsResult {
        @AuraEnabled public Database.Cursor cursor;
        @AuraEnabled public Database.PaginationCursor paginationCursor;
        @AuraEnabled public List<Account> records;
        @AuraEnabled public Integer offset;
        @AuraEnabled public Boolean hasMore;
        @AuraEnabled public Integer totalRecords;
        @AuraEnabled public Integer deletedRows;
        @AuraEnabled public Boolean usingSessionCache;
        @AuraEnabled public CursorLimitsInfo limitsInfo;
    }

    public class CursorLimitsInfo {
        @AuraEnabled public Integer apexCursors;
        @AuraEnabled public Integer limitApexCursors;
        @AuraEnabled public Integer apexCursorRows;
        @AuraEnabled public Integer limitApexCursorRows;
        @AuraEnabled public Integer apexPaginationCursors;
        @AuraEnabled public Integer limitApexPaginationCursors;
        @AuraEnabled public Integer apexPaginationCursorRows;
        @AuraEnabled public Integer limitApexPaginationCursorRows;
        @AuraEnabled public Integer fetchCallsOnApexCursor;
        @AuraEnabled public Integer limitFetchCallsOnApexCursor;
        @AuraEnabled public Integer dailyApexCursors;
        @AuraEnabled public Integer limitDailyApexCursors;
        @AuraEnabled public Integer dailyApexPaginationCursors;
        @AuraEnabled public Integer limitDailyApexPaginationCursors;
        @AuraEnabled public Integer dailyApexCursorRows;
        @AuraEnabled public Integer limitDailyApexCursorRows;
    }
}
