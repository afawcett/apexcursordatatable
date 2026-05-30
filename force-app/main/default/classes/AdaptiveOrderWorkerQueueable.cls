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

    /**
     * @description Creates a worker for one chunk of the adaptive async run.
     * @param runId Correlates platform events with the LWC run.
     * @param cursor Shared cursor opened by {@link AdaptiveAsyncController}.
     * @param sequence One-based chunk sequence for telemetry.
     */
    public AdaptiveOrderWorkerQueueable(String runId, Database.Cursor cursor, Integer sequence) {
        this.runId = runId;
        this.cursor = cursor;
        this.startIndex = 0;
        this.sequence = sequence;
        this.totalRows = cursor.getNumRecords();
    }

    /**
     * @description Processes the next cursor chunk and chains another job when needed.
     * @param context Queueable context for this execution.
     */
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

    /**
     * @description Publishes chunk telemetry after the queueable transaction commits.
     * @param context Finalizer context for the parent queueable job.
     */
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
     * @description Reads forward from {@code startIndex}, adding orders until the chunk is full.
     * Fetch batch size is capped by callout budget so we do not pull rows we will not pack.
     * @return Orders and callout counts packed for this queueable execution.
     */
    private ExecuteScope fetchChunk() {
        ExecuteScope scope = new ExecuteScope();
        Integer calloutBudget = Limits.getLimitCallouts() - Limits.getCallouts();
        Integer pos = startIndex;
        while (pos < totalRows) {
            Integer remaining = totalRows - pos;
            Integer batchSize = scope.predictedCallouts >= calloutBudget ? 1 :
                Math.min(MAX_CURSOR_FETCH_SIZE, Math.min(remaining, calloutBudget - scope.predictedCallouts + 1));
            for (Order row : (List<Order>) cursor.fetch(pos, batchSize)) {
                Integer rowCallouts = rowCalloutsFor(row);
                Boolean withinCalloutBudget =
                    scope.orders.isEmpty() || scope.predictedCallouts + rowCallouts <= calloutBudget;
                Boolean stillInCalloutSegment =
                    scope.predictedCallouts < calloutBudget || rowCallouts > 0;
                if (withinCalloutBudget && stillInCalloutSegment) {
                    scope.orders.add(row);
                    scope.predictedCallouts += rowCallouts;
                    scope.calloutOrders += rowCallouts;
                    scope.zeroCalloutOrders += (1 - rowCallouts);
                    pos++;
                } else {
                    return scope;
                }
            }
        }
        return scope;
    }

    /** @description Thrown when the org queueable chain depth limit is reached. */
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
