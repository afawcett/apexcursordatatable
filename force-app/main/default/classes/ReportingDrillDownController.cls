/**
 * Reporting drill-down demo: monthly chart points from pagination cursor fetchPage
 * (mid-month, one fetch per month) plus session cursor for daily drill-down.
 */
public with sharing class ReportingDrillDownController {
    private static final Set<String> ALLOWED_PRODUCTS = new Set<String>{ 'RAM', 'CPU' };
    private static final String DAILY_SOQL =
        'SELECT Id, EffectiveDate__c, Value__c, Product__c ' +
        'FROM UnitPriceObservation__c WHERE Product__c = :product ORDER BY EffectiveDate__c ASC';
    private static final Integer MID_MONTH_DAY = 15;
    private static final Integer MAX_CURSOR_FETCHES_PER_INIT = 100;

    private static String sessionKey(String product) {
        return 'reportingDrillDownPC' + product;
    }

    private static void validateProduct(String product) {
        if (product == null || !ALLOWED_PRODUCTS.contains(product)) {
            throw new AuraHandledException('Invalid product. Use RAM or CPU.');
        }
    }

    /**
     * Builds monthly chart points via cursor fetchPage and stores pagination cursor in session.
     */
    @AuraEnabled(cacheable=false)
    public static ChartSeriesResult initializeSeries(String product) {
        validateProduct(product);
        return buildSeries(product);
    }

    /**
     * Clears the session cursor and rebuilds chart + cursor.
     */
    @AuraEnabled(cacheable=false)
    public static ChartSeriesResult refreshSeries(String product) {
        validateProduct(product);
        Cache.Session.remove(sessionKey(product));
        return buildSeries(product);
    }

    /**
     * Fetches daily rows for inclusive cursor index range via session pagination cursor.
     */
    @AuraEnabled(cacheable=false)
    public static DetailRangeResult fetchDetailRange(String product, Integer startIndex, Integer endIndex) {
        validateProduct(product);
        if (startIndex == null || endIndex == null || startIndex < 0 || endIndex < startIndex) {
            throw new AuraHandledException('Invalid index range.');
        }

        Database.PaginationCursor paginationCursor =
            (Database.PaginationCursor) Cache.Session.get(sessionKey(product));
        if (paginationCursor == null) {
            throw new AuraHandledException('No cursor in session. Click Refresh to initialize.');
        }

        Integer total = paginationCursor.getNumRecords();
        if (total == 0) {
            return emptyDetailResult(startIndex, endIndex);
        }

        Integer safeStart = Math.min(startIndex, total - 1);
        Integer safeEnd = Math.min(endIndex, total - 1);
        Integer count = safeEnd - safeStart + 1;
        Integer fetchSize = count > 0 ? Math.min(count, total - safeStart) : 0;

        DetailRangeResult result = new DetailRangeResult();
        result.startIndex = safeStart;
        result.endIndex = safeEnd;

        if (fetchSize > 0) {
            Database.CursorFetchResult fetchResult = paginationCursor.fetchPage(safeStart, fetchSize);
            result.deletedRows = fetchResult.getNumDeletedRecords();
            for (SObject row : fetchResult.getRecords()) {
                UnitPriceObservation__c obs = (UnitPriceObservation__c) row;
                ObservationRow detail = new ObservationRow();
                detail.effectiveDate = obs.EffectiveDate__c;
                detail.value = obs.Value__c;
                detail.product = obs.Product__c;
                result.records.add(detail);
            }
        }
        return result;
    }

    private static ChartSeriesResult buildSeries(String product) {
        ChartSeriesResult result = new ChartSeriesResult();
        result.product = product;
        result.monthlyPoints = new List<MonthlyPoint>();
        result.cursorFetchCount = 0;

        Database.PaginationCursor paginationCursor =
            Database.getPaginationCursor(DAILY_SOQL, AccessLevel.USER_MODE);
        Cache.Session.put(sessionKey(product), paginationCursor);

        Integer total = paginationCursor.getNumRecords();
        result.dailyRowCount = total;
        if (total == 0) {
            return result;
        }

        Integer fetchCalls = 0;

        Database.CursorFetchResult firstChunk = paginationCursor.fetchPage(0, 1);
        fetchCalls++;
        Date rangeStart = ((UnitPriceObservation__c) firstChunk.getRecords()[0]).EffectiveDate__c;

        Database.CursorFetchResult lastChunk = paginationCursor.fetchPage(total - 1, 1);
        fetchCalls++;
        Date rangeEnd = ((UnitPriceObservation__c) lastChunk.getRecords()[0]).EffectiveDate__c;

        result.rangeStart = rangeStart;
        result.rangeEnd = rangeEnd;

        Date monthCursor = Date.newInstance(rangeStart.year(), rangeStart.month(), 1);
        Date endMonth = Date.newInstance(rangeEnd.year(), rangeEnd.month(), 1);

        while (monthCursor <= endMonth && fetchCalls < MAX_CURSOR_FETCHES_PER_INIT) {
            Integer year = monthCursor.year();
            Integer month = monthCursor.month();
            Integer targetDay = Math.min(MID_MONTH_DAY, Date.daysInMonth(year, month));
            Date midMonth = Date.newInstance(year, month, targetDay);

            if (midMonth >= rangeStart && midMonth <= rangeEnd) {
                Integer dayIndex = rangeStart.daysBetween(midMonth);
                if (dayIndex >= 0 && dayIndex < total) {
                    Database.CursorFetchResult midChunk = paginationCursor.fetchPage(dayIndex, 1);
                    fetchCalls++;
                    if (!midChunk.getRecords().isEmpty()) {
                        UnitPriceObservation__c obs = (UnitPriceObservation__c) midChunk.getRecords()[0];
                        MonthlyPoint point = new MonthlyPoint();
                        point.effectiveDate = obs.EffectiveDate__c;
                        point.value = obs.Value__c;
                        point.dayIndex = dayIndex;
                        result.monthlyPoints.add(point);
                    }
                }
            }
            monthCursor = monthCursor.addMonths(1);
        }

        result.cursorFetchCount = fetchCalls;
        return result;
    }

    private static DetailRangeResult emptyDetailResult(Integer startIndex, Integer endIndex) {
        DetailRangeResult result = new DetailRangeResult();
        result.startIndex = startIndex;
        result.endIndex = endIndex;
        result.records = new List<ObservationRow>();
        result.deletedRows = 0;
        return result;
    }

    public class ChartSeriesResult {
        @AuraEnabled public String product;
        @AuraEnabled public List<MonthlyPoint> monthlyPoints;
        @AuraEnabled public Date rangeStart;
        @AuraEnabled public Date rangeEnd;
        @AuraEnabled public Integer dailyRowCount;
        @AuraEnabled public Integer cursorFetchCount;
    }

    public class MonthlyPoint {
        @AuraEnabled public Date effectiveDate;
        @AuraEnabled public Decimal value;
        @AuraEnabled public Integer dayIndex;
    }

    public class DetailRangeResult {
        @AuraEnabled public List<ObservationRow> records;
        @AuraEnabled public Integer startIndex;
        @AuraEnabled public Integer endIndex;
        @AuraEnabled public Integer deletedRows;

        public DetailRangeResult() {
            this.records = new List<ObservationRow>();
        }
    }

    public class ObservationRow {
        @AuraEnabled public Date effectiveDate;
        @AuraEnabled public Decimal value;
        @AuraEnabled public String product;
    }
}
