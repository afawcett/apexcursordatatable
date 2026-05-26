/**
 * Asserts documented Pagination Cursor behavior (apex_cursors.htm).
 * Expectation: partial final page returns remaining records; fetchPage after deletes skips deleted rows. No exception.
 * Current outcome: both throw InvalidParameterValueException "Fetch beyond bound detected: 100".
 * @see https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_cursors.htm
 */
@IsTest
private class PaginationCursorBugTest {

    private static final Integer PAGE_SIZE = 50;
    private static final Integer TOTAL_RECORDS = 53;

    @TestSetup
    static void setup() {
        List<Account> accounts = new List<Account>();
        for (Integer i = 0; i < TOTAL_RECORDS; i++) {
            accounts.add(new Account(
                Name = 'PaginationCursorBugTest_' + String.valueOf(i).leftPad(4, '0'),
                Industry = 'Technology',
                Type = 'Customer'
            ));
        }
        insert accounts;
    }

    /**
     * Partial final page — uses raw PAGE_SIZE for last page (start+pageSize > totalRecords).
     * Documented: fetchPage returns "a partial, final page of results" when the cursor reaches the end before pageSize.
     * Expectation: fetchPage(50, 50) with 53 total returns 3 records, no exception.
     * Current outcome: InvalidParameterValueException "Fetch beyond bound detected: 100".
     */
    @IsTest
    static void fetchPagePartialLastPageReturnsRemainingRecordsPerDocs() {
        // Given: 53 records, page size 50 → last page has 3 records
        Database.PaginationCursor cursor = Database.getPaginationCursor(
            'SELECT Id, Name FROM Account WHERE Name LIKE \'PaginationCursorBugTest_%\' ORDER BY Name',
            AccessLevel.USER_MODE
        );
        Database.CursorFetchResult page1 = cursor.fetchPage(0, PAGE_SIZE);
        Integer startLastPage = page1.getNextIndex();
        Integer pageSizeForLastPage = PAGE_SIZE;

        // When: Fetch final page
        Database.CursorFetchResult page2 = null;
        Exception caught = null;
        try {
            page2 = cursor.fetchPage(startLastPage, pageSizeForLastPage);
        } catch (Exception e) {
            caught = e;
        }

        // Then: No exception, 3 records
        System.assert(caught == null, 'Partial final page should return remaining records, not throw. Got: ' + (caught != null ? caught.getMessage() : ''));
        System.assertEquals(3, page2.getRecords().size(), 'Partial final page should have 3 records');
    }

    /**
     * Same as above but caller caps page size so start + pageSize <= totalRecords (DX workaround).
     * Expectation: fetchPage(50, 3) returns 3 records, no exception.
     */
    @IsTest
    static void fetchPagePartialLastPageReturnsRemainingRecordsPerDocsVariant() {
        // Given: 53 records, page size 50 → last page has 3 records
        Database.PaginationCursor cursor = Database.getPaginationCursor(
            'SELECT Id, Name FROM Account WHERE Name LIKE \'PaginationCursorBugTest_%\' ORDER BY Name',
            AccessLevel.USER_MODE
        );
        Database.CursorFetchResult page1 = cursor.fetchPage(0, PAGE_SIZE);
        Integer startLastPage = page1.getNextIndex();
        Integer pageSizeForLastPage = Math.min(PAGE_SIZE, cursor.getNumRecords() - startLastPage);

        // When: Fetch final page
        Database.CursorFetchResult page2 = null;
        Exception caught = null;
        try {
            page2 = cursor.fetchPage(startLastPage, pageSizeForLastPage);
        } catch (Exception e) {
            caught = e;
        }

        // Then: No exception, 3 records
        System.assert(caught == null, 'Partial final page should return remaining records, not throw. Got: ' + (caught != null ? caught.getMessage() : ''));
        System.assertEquals(3, page2.getRecords().size(), 'Partial final page should have 3 records');
    }

    /**
     * Deleted records during cursor use.
     * Documented: "Record rows deleted after the creation of the cursor are skipped over by default"; same indexing as when cursor was created.
     * Expectation: After deleting first 10 rows, fetchPage(50, 50) returns the 3 remaining rows at positions 50–52 (partial page), no exception.
     * Current outcome: InvalidParameterValueException "Fetch beyond bound detected: 100".
     */
    @IsTest
    static void fetchPageAfterRecordsDeletedSkipsDeletedAndReturnsPagePerDocs() {
        // Given: 53 records, cursor created, first page fetched; then first 10 deleted (43 remain; positions 50–52 still exist)
        Database.PaginationCursor cursor = Database.getPaginationCursor(
            'SELECT Id, Name FROM Account WHERE Name LIKE \'PaginationCursorBugTest_%\' ORDER BY Name',
            AccessLevel.USER_MODE
        );
        cursor.fetchPage(0, PAGE_SIZE);
        delete [SELECT Id FROM Account WHERE Name LIKE :('PaginationCursorBugTest_' + '%') ORDER BY Name LIMIT 10];

        // When: Next page (start=50, pageSize=50); same indexing — only 3 rows at 50–52 remain
        Database.CursorFetchResult page2 = null;
        Exception caught = null;
        try {
            page2 = cursor.fetchPage(50, PAGE_SIZE);
        } catch (Exception e) {
            caught = e;
        }

        // Then: Per docs, same indexing; we get fewer records this page (partial page of 3)
        System.assert(caught == null, 'Documented: fetchPage after deletes should skip deleted and return partial page, not throw. Got: ' + (caught != null ? caught.getMessage() : ''));
        System.assertEquals(3, page2.getRecords().size(), 'Partial page should have 3 records (positions 50–52)');
    }

    /**
     * Same as above but caller caps page size so start + pageSize <= totalRecords (DX workaround).
     * Expectation: fetchPage(50, 3) returns 3 records, no exception.
     */
    @IsTest
    static void fetchPageAfterRecordsDeletedSkipsDeletedAndReturnsPagePerDocsVariant() {
        // Given: 53 records, cursor created, first page fetched; then first 10 deleted (43 remain; positions 50–52 still exist)
        Database.PaginationCursor cursor = Database.getPaginationCursor(
            'SELECT Id, Name FROM Account WHERE Name LIKE \'PaginationCursorBugTest_%\' ORDER BY Name',
            AccessLevel.USER_MODE
        );
        cursor.fetchPage(0, PAGE_SIZE);
        delete [SELECT Id FROM Account WHERE Name LIKE :('PaginationCursorBugTest_' + '%') ORDER BY Name LIMIT 10];

        Integer startNextPage = 50;
        Integer pageSizeForNextPage = Math.min(PAGE_SIZE, cursor.getNumRecords() - startNextPage);

        // When: Next page with capped size
        Database.CursorFetchResult page2 = null;
        Exception caught = null;
        try {
            page2 = cursor.fetchPage(startNextPage, pageSizeForNextPage);
        } catch (Exception e) {
            caught = e;
        }

        // Then: No exception, 3 records
        System.assert(caught == null, 'fetchPage after deletes with capped size should return partial page, not throw. Got: ' + (caught != null ? caught.getMessage() : ''));
        System.assertEquals(3, page2.getRecords().size(), 'Partial page should have 3 records (positions 50–52)');
    }
}
