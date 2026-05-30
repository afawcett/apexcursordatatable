/**
 * LWC entry point for the Adaptive Async demo tab.
 * Opens one {@link Database.Cursor} per run and enqueues {@link AdaptiveOrderWorkerQueueable}.
 */
public with sharing class AdaptiveAsyncController {
    /** Chained chunk count for the demo dataset (5 segments); org default is often 5. */
    private static final Integer QUEUEABLE_STACK_DEPTH = 10;
    private static final Set<String> CURSOR_ORDER_FIELDS = new Set<String>{
        'External_Id__c',
        'Shipping_Country__c'
    };

    @AuraEnabled
    public static RunInfo startRun(String orderByField) {
        String orderField = normalizeOrderByField(orderByField);

        Integer totalOrders = [SELECT COUNT() FROM Order WHERE External_Id__c LIKE 'ADAPT-ORD-%'];
        if (totalOrders == 0) {
            throw new AuraHandledException(
                'No demo orders. Run: node scripts/generate-adaptive-orders.mjs --load'
            );
        }

        String runId = UUID.randomUUID().toString();
        Database.Cursor cursor = Database.getCursor(
            'SELECT Id, External_Id__c, Shipping_Country__c, Contains_Hazmat__c, Digital__c ' +
                'FROM Order WHERE External_Id__c LIKE \'ADAPT-ORD-%\' ORDER BY ' +
                orderField,
            AccessLevel.USER_MODE
        );
        AsyncOptions options = new AsyncOptions();
        options.MaximumQueueableStackDepth = QUEUEABLE_STACK_DEPTH;
        System.enqueueJob(new AdaptiveOrderWorkerQueueable(runId, cursor, 1), options);

        RunInfo info = new RunInfo();
        info.runId = runId;
        info.totalOrders = totalOrders;
        info.maxCalloutsPerChunk = Limits.getLimitCallouts();
        info.orderByField = orderField;
        return info;
    }

    private static String normalizeOrderByField(String orderByField) {
        if (String.isBlank(orderByField) || !CURSOR_ORDER_FIELDS.contains(orderByField)) {
            return 'External_Id__c';
        }
        return orderByField;
    }

    @AuraEnabled(cacheable=true)
    public static Integer getDemoOrderCount() {
        return [SELECT COUNT() FROM Order WHERE External_Id__c LIKE 'ADAPT-ORD-%'];
    }

    /** Returned to the LWC when a run starts (progress bar and empApi filter). */
    public class RunInfo {
        @AuraEnabled public String runId;
        @AuraEnabled public Integer totalOrders;
        @AuraEnabled public Integer maxCalloutsPerChunk;
        @AuraEnabled public String orderByField;
    }
}
