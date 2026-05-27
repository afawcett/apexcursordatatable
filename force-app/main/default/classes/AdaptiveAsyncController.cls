/**
 * LWC entry point for the Adaptive Async demo tab.
 * Opens one {@link Database.Cursor} per run and enqueues {@link AdaptiveOrderWorkerQueueable}.
 */
public with sharing class AdaptiveAsyncController {
    /** Chained chunk count for the demo dataset (5 segments); org default is often 5. */
    private static final Integer QUEUEABLE_STACK_DEPTH = 10;
    @AuraEnabled
    public static RunInfo startRun() {
        Integer totalOrders = [SELECT COUNT() FROM Order WHERE External_Id__c LIKE 'ADAPT-ORD-%'];
        if (totalOrders == 0) {
            throw new AuraHandledException(
                'No demo orders. Run: node scripts/generate-adaptive-orders.mjs --load'
            );
        }

        String runId = UUID.randomUUID().toString();
        Database.Cursor cursor = Database.getCursor(
            'SELECT Id, Shipping_Country__c, Contains_Hazmat__c, Digital__c ' +
                'FROM Order WHERE External_Id__c LIKE \'ADAPT-ORD-%\' ORDER BY External_Id__c',
            AccessLevel.USER_MODE
        );
        AsyncOptions options = new AsyncOptions();
        options.MaximumQueueableStackDepth = QUEUEABLE_STACK_DEPTH;
        System.enqueueJob(new AdaptiveOrderWorkerQueueable(runId, cursor, 1), options);

        RunInfo info = new RunInfo();
        info.runId = runId;
        info.totalOrders = totalOrders;
        info.maxCalloutsPerChunk = Limits.getLimitCallouts();
        return info;
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
    }
}
