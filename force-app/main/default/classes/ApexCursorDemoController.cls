/**
 * Apex controller for the apexCursorDemo LWC infinite-scroll datatable.
 * Demonstrates standard Database.Cursor and Database.PaginationCursor paging,
 * optional session-cache storage, and cursor limit reporting.
 */
public with sharing class ApexCursorDemoController {
    private static final String SESSION_STANDARD_CURSOR_KEY = 'apexCursorDemoStandard';
    private static final String SESSION_PAGINATION_CURSOR_KEY = 'apexCursorDemoPagination';
    private static final String ACCOUNT_SOQL =
        'SELECT Id, Name, Industry, Type, BillingCity, Phone FROM Account WHERE Name LIKE \'TEST%\' ORDER BY Name';

    /**
     * Loads the next batch of Account records using a standard Apex cursor.
     *
     * @param cursor Cursor from the prior response; ignored when useSessionCache is true.
     * @param offset Row index to fetch from.
     * @param batchSize Maximum rows to return.
     * @param useSessionCache true = session cache, false = LWC-held cursor, null = auto-detect from session.
     * @return Page of records, updated cursor state, and current limit usage.
     */
    @AuraEnabled(cacheable=false)
    public static LoadMoreRecordsResult loadMoreRecords(
        Database.Cursor cursor,
        Integer offset,
        Integer batchSize,
        Boolean useSessionCache
    ) {
        try {
            // null means auto: use session cache when a cursor is already stored for this user session.
            useSessionCache = useSessionCache != null ? useSessionCache : Cache.Session.get(SESSION_STANDARD_CURSOR_KEY) != null;
            Boolean usingSessionCache = false;
            if (useSessionCache == true) {
                // Cursor lives in Cache.Session so it survives across Apex transactions.
                cursor = (Database.Cursor) Cache.Session.get(SESSION_STANDARD_CURSOR_KEY);
                if (cursor == null) {
                    cursor = Database.getCursor(ACCOUNT_SOQL, AccessLevel.USER_MODE);
                    Cache.Session.put(SESSION_STANDARD_CURSOR_KEY, cursor);
                }
                usingSessionCache = true;
            } else {
                // Explicit off: clear session and rely on the cursor serialized back to the LWC.
                Cache.Session.remove(SESSION_STANDARD_CURSOR_KEY);
                if (cursor == null) {
                    cursor = Database.getCursor(ACCOUNT_SOQL, AccessLevel.USER_MODE);
                }
            }

            LoadMoreRecordsResult result = new LoadMoreRecordsResult();
            result.cursor = cursor;
            // Fetch the next batch from the current offset.
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

    /**
     * Loads the next batch of Account records using a pagination cursor.
     * Pagination cursors track deleted rows and expose fetchPage for index-based paging.
     *
     * @param paginationCursor Cursor from the prior response; ignored when useSessionCache is true.
     * @param start Row index to fetch from.
     * @param pageSize Maximum rows to return.
     * @param useSessionCache true = session cache, false = LWC-held cursor, null = auto-detect from session.
     * @return Page of records, updated cursor state, deleted-row count, and current limit usage.
     */
    @AuraEnabled(cacheable=false)
    public static LoadMoreRecordsResult loadMoreRecordsWithPagination(
        Database.PaginationCursor paginationCursor,
        Integer start,
        Integer pageSize,
        Boolean useSessionCache
    ) {
        try {
            // null means auto: use session cache when a cursor is already stored for this user session.
            useSessionCache = useSessionCache != null ? useSessionCache : Cache.Session.get(SESSION_PAGINATION_CURSOR_KEY) != null;
            Boolean usingSessionCache = false;
            if (useSessionCache == true) {
                // Cursor lives in Cache.Session so it survives across Apex transactions.
                paginationCursor = (Database.PaginationCursor) Cache.Session.get(SESSION_PAGINATION_CURSOR_KEY);
                if (paginationCursor == null) {
                    paginationCursor = Database.getPaginationCursor(ACCOUNT_SOQL, AccessLevel.USER_MODE);
                    Cache.Session.put(SESSION_PAGINATION_CURSOR_KEY, paginationCursor);
                }
                usingSessionCache = true;
            } else {
                // Explicit off: clear session and rely on the cursor serialized back to the LWC.
                Cache.Session.remove(SESSION_PAGINATION_CURSOR_KEY);
                if (paginationCursor == null) {
                    paginationCursor = Database.getPaginationCursor(ACCOUNT_SOQL, AccessLevel.USER_MODE);
                }
            }

            LoadMoreRecordsResult result = new LoadMoreRecordsResult();
            // Fetch the next page from the current start index.
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

    /**
     * Captures transaction-scoped cursor limits and daily org-wide cursor limits
     * for display in the demo UI.
     */
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

        // Daily limits are org-wide counters, not per-transaction.
        Map<String, System.OrgLimit> limitMap = OrgLimits.getMap();
        System.OrgLimit dailyCursorLimit = limitMap.get('DailyApexCursorLimit');
        System.OrgLimit dailyPaginationCursorLimit = limitMap.get('DailyApexPCursorLimit');
        System.OrgLimit dailyCursorRowsLimit = limitMap.get('DailyApexCursorRowsLimit');
        info.dailyApexCursors = dailyCursorLimit?.getValue();
        info.limitDailyApexCursors = dailyCursorLimit?.getLimit();
        info.dailyApexPaginationCursors = dailyPaginationCursorLimit?.getValue();
        info.limitDailyApexPaginationCursors = dailyPaginationCursorLimit?.getLimit();
        info.dailyApexCursorRows = dailyCursorRowsLimit?.getValue();
        info.limitDailyApexCursorRows = dailyCursorRowsLimit?.getLimit();
        return info;
    }

    /** AuraEnabled response for a single infinite-scroll page load. */
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

    /** Transaction and daily cursor limit counters returned with each page load. */
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
