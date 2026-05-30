/**
 * Chains queueable jobs over one {@link Database.Cursor}, packing each chunk to stay within the
 * org HTTP callout limit. Chunk telemetry is published from a {@link System.Finalizer} after each
 * queueable transaction commits.
 *
 * The cursor is created in {@link AdaptiveAsyncController} and passed in. Each {@code System.enqueueJob(this)}
 * serializes the job instance (including {@code startIndex} and the cursor), so chained links keep
 * position without {@link Database.Stateful} — that interface is for Batch Apex only.
 */
public with sharing class AdaptiveOrderWorkerQueueable implements Queueable, Database.AllowsCallouts, System.Finalizer {

    /** Platform max rows per {@code Cursor.fetch} (same cap as pagination {@code fetchPage}). */
    private static final Integer MAX_CURSOR_FETCH_SIZE = 2000;

    private Database.Cursor cursor;
    private final String runId;
    private Integer startIndex;
    private Integer sequence;
    private Integer eventSequence;
    private final Integer totalRows;

    private Integer plannedChunkSize;
    private Integer predictedCallouts;
    private Integer calloutOrders;
    private Integer zeroCalloutOrders;
    private Boolean success;
    private String errorMessage;
    private Boolean runComplete;

    public AdaptiveOrderWorkerQueueable(String runId, Database.Cursor cursor, Integer sequence) {
        this.runId = runId;
        this.cursor = cursor;
        this.startIndex = 0;
        this.sequence = sequence;
        this.totalRows = cursor.getNumRecords();
    }

    public void execute(QueueableContext context) {
        // Publish chunk telemetry after this transaction commits (success or failure).
        System.attachFinalizer(this);
        eventSequence = sequence;

        // Pack the next slice of cursor rows without exceeding Limits.getLimitCallouts().
        ExecuteScope scope = fetchChunk();
        List<Order> chunk = scope.orders;

        // Simulate integration CPU (hazmat / international add cost; not used for chunk sizing).
        for (Order row : chunk) {
            Decimal sink = 0;
            Integer iterations = row.Contains_Hazmat__c == true ? 1200 : 400;
            if (row.Shipping_Country__c != 'USA') {
                iterations += 800;
            }
            for (Integer i = 0; i < iterations; i++) {
                sink += Math.sqrt(i + 1);
            }
        }

        // Advance past this chunk; moreOrders drives chaining and runComplete.
        startIndex += chunk.size();
        Boolean moreOrders = startIndex < totalRows;

        // Finalizer publishes these after each queueable transaction.
        plannedChunkSize = chunk.size();
        predictedCallouts = scope.predictedCallouts;
        calloutOrders = scope.calloutOrders;
        zeroCalloutOrders = scope.zeroCalloutOrders;
        success = true;

        // Cannot chain another job when the org queueable stack depth is exhausted.
        if (moreOrders && AsyncInfo.getCurrentQueueableStackDepth() >= AsyncInfo.getMaximumQueueableStackDepth()) {
            runComplete = true;
            throw new AdaptiveAsyncChainLimitException(
                'Queueable chain depth limit reached; start another run to continue.'
            );
        }

        runComplete = !moreOrders;
        if (moreOrders) {
            sequence++;
            System.enqueueJob(this);
        }
    }

    public void execute(FinalizerContext context) {
        if (context.getResult() == ParentJobResult.UNHANDLED_EXCEPTION) {
            success = false;
            errorMessage = context.getException() != null
                ? context.getException().getMessage()
                : 'Queueable failed with an unhandled exception.';
        }

        EventBus.publish(
            new AdaptiveAsyncChunk__e(
                Run_Id__c = runId,
                Sequence__c = eventSequence,
                Planned_Chunk_Size__c = plannedChunkSize,
                Actual_Processed__c = plannedChunkSize,
                Predicted_Callouts__c = predictedCallouts,
                Callout_Orders__c = calloutOrders,
                Zero_Callout_Orders__c = zeroCalloutOrders,
                Job_Id__c = String.valueOf(context.getAsyncApexJobId()),
                Success__c = success,
                Error_Message__c = errorMessage,
                Run_Complete__c = runComplete
            )
        );
    }

    /**
     * Reads forward from {@code startIndex}, adding orders until the chunk is full.
     * Fetch batch size is capped by callout budget so we do not pull rows we will not pack.
     */
    private ExecuteScope fetchChunk() {
        ExecuteScope scope = new ExecuteScope();
        Integer calloutBudget = Limits.getLimitCallouts() - Limits.getCallouts();
        Integer pos = startIndex;

        while (pos < totalRows) {
            Integer remaining = totalRows - pos;
            Integer batchSize = remaining;
            if (scope.predictedCallouts >= calloutBudget) {
                // Budget full: read one row at a time until we hit the next segment (zero callouts).
                batchSize = 1;
            } else {
                // At most enough rows to exhaust remaining callout budget (+1 to detect overflow).
                Integer calloutRowsLeft = calloutBudget - scope.predictedCallouts + 1;
                batchSize = Math.min(MAX_CURSOR_FETCH_SIZE, Math.min(remaining, calloutRowsLeft));
            }

            for (Order row : (List<Order>) cursor.fetch(pos, batchSize)) {
                // Predicted HTTP callouts for this row: digital = 0, USA = 0, non-USA = 1.
                Integer rowCallouts = rowCalloutsFor(row);
                if (!scope.orders.isEmpty() && scope.predictedCallouts + rowCallouts > calloutBudget) {
                    return scope;
                }
                // Callout budget full: stop before the next zero-callout row (start of the following chunk).
                if (scope.predictedCallouts >= calloutBudget && rowCallouts == 0) {
                    return scope;
                }
                scope.orders.add(row);
                scope.predictedCallouts += rowCallouts;
                if (rowCallouts == 0) {
                    scope.zeroCalloutOrders++;
                } else {
                    scope.calloutOrders++;
                }
                pos++;
            }
        }
        return scope;
    }

    public class AdaptiveAsyncChainLimitException extends Exception {
    }

    /** Orders packed and counted in the current queueable execution. */
    private class ExecuteScope {
        List<Order> orders = new List<Order>();
        Integer predictedCallouts = 0;
        Integer calloutOrders = 0;
        Integer zeroCalloutOrders = 0;
    }

    private static Integer rowCalloutsFor(Order row) {
        return row.Digital__c == true ? 0 : (row.Shipping_Country__c != 'USA' ? 1 : 0);
    }
}
