/**
 * Self-contained script to reproduce the Pagination Cursor bugs discussed in blog comments:
 * https://andyinthecloud.com/2026/01/19/improved-infinite-data-scrolling-with-new-apex-pagination-cursors-ga/
 *
 * Bug 1: fetchPage(start, pageSize) requires (start + pageSize) <= totalRecords.
 *        When total records is not a multiple of pageSize (e.g. 53 records, page 50),
 *        the last fetch (start=50, pageSize=50) throws because 50+50=100 > 53,
 *        so the last 3 records are never returned.
 *
 * Bug 2: If records are deleted after the cursor is created, the cursor's getNumRecords()
 *        still reflects the original count. A client uses that to decide the next fetch;
 *        the last fetch can then exceed the actual row count and throw.
 *
 * Run: sf apex run --file apex/ReproducePaginationCursorBug.apex
 */
final String PREFIX = 'CURSOR_BUG_TEST_';
final Integer PAGE_SIZE = 50;

// ========== TEARDOWN: Remove any leftover test data ==========
List<Account> toDelete = [SELECT Id FROM Account WHERE Name LIKE :(PREFIX + '%') WITH USER_MODE];
if (!toDelete.isEmpty()) {
    delete toDelete;
    System.debug('Teardown: Deleted ' + toDelete.size() + ' existing CURSOR_BUG_TEST_ accounts.');
}

// ========== CREATE DATA: Exactly 53 records (one full page of 50 + partial page of 3) ==========
Integer totalRecords = 53;
List<Account> accounts = new List<Account>();
for (Integer i = 0; i < totalRecords; i++) {
    accounts.add(new Account(
        Name = PREFIX + String.valueOf(i).leftPad(4, '0'),
        Industry = 'Technology',
        Type = 'Customer'
    ));
}
insert accounts;
System.debug('Created ' + totalRecords + ' accounts. Page size = ' + PAGE_SIZE + ', so last page has ' + (totalRecords - PAGE_SIZE) + ' records.');

// ========== BUG 1: Partial last page ==========
System.debug('--- BUG 1: Partial last page (start+pageSize > totalRecords) ---');
Database.PaginationCursor cursor = Database.getPaginationCursor(
    'SELECT Id, Name FROM Account WHERE Name LIKE \'' + PREFIX + '%\' ORDER BY Name',
    AccessLevel.USER_MODE
);
Integer totalFromCursor = cursor.getNumRecords();
System.debug('Cursor reports totalRecords = ' + totalFromCursor + ' (expected ' + totalRecords + ')');

// First page: start=0, count=50 -> OK (0+50 <= 53)
Database.CursorFetchResult page1 = cursor.fetchPage(0, PAGE_SIZE);
System.debug('Fetch 1: fetchPage(0, ' + PAGE_SIZE + ') -> got ' + page1.getRecords().size() + ' records, nextIndex=' + page1.getNextIndex());

// Last page: start=50, count=50 -> (50+50)=100 > 53. Per Fabrice: this throws instead of returning 3 records.
Integer startLastPage = page1.getNextIndex(); // 50
System.debug('Fetch 2: about to call fetchPage(' + startLastPage + ', ' + PAGE_SIZE + '). (start+pageSize)=' + (startLastPage + PAGE_SIZE) + ', totalRecords=' + totalFromCursor + '. Expect error if (start+pageSize) > totalRecords.');
try {
    Database.CursorFetchResult page2 = cursor.fetchPage(startLastPage, PAGE_SIZE);
    System.debug('Fetch 2: unexpectedly succeeded. Got ' + page2.getRecords().size() + ' records.');
} catch (Exception e) {
    System.debug('Fetch 2: REPRODUCED BUG 1 - Exception: ' + e.getTypeName() + ' - ' + e.getMessage());
    System.debug('Stack: ' + e.getStackTraceString());
}

// ========== BUG 2: Deleted records during cursor ==========
System.debug('--- BUG 2: Records deleted after cursor created ---');
Database.PaginationCursor cursor2 = Database.getPaginationCursor(
    'SELECT Id, Name FROM Account WHERE Name LIKE \'' + PREFIX + '%\' ORDER BY Name',
    AccessLevel.USER_MODE
);
Integer totalBeforeDelete = cursor2.getNumRecords();
page1 = cursor2.fetchPage(0, PAGE_SIZE);
System.debug('Created second cursor, totalRecords=' + totalBeforeDelete + ', fetched first page.');

// Delete 10 records so actual count becomes 43. Cursor still thinks total = 53.
List<Account> deleteSome = [SELECT Id FROM Account WHERE Name LIKE :(PREFIX + '%') ORDER BY Name LIMIT 10];
delete deleteSome;
System.debug('Deleted ' + deleteSome.size() + ' records. Actual count now 43; cursor still reports ' + totalBeforeDelete + '.');

// Client would do next fetch with start=50, pageSize=50 (hasMore = 50 < 53). But only 43 rows exist -> 50+50 > 43.
System.debug('Simulating next fetch: fetchPage(50, 50). Actual rows=43, so (50+50) > 43.');
try {
    Database.CursorFetchResult page2 = cursor2.fetchPage(50, PAGE_SIZE);
    System.debug('Fetch after delete: unexpectedly succeeded. Got ' + page2.getRecords().size() + ' records.');
} catch (Exception e) {
    System.debug('REPRODUCED BUG 2 - Exception: ' + e.getTypeName() + ' - ' + e.getMessage());
}

// ========== TEARDOWN: Remove test data ==========
toDelete = [SELECT Id FROM Account WHERE Name LIKE :(PREFIX + '%') WITH USER_MODE];
delete toDelete;
System.debug('Teardown: Deleted ' + toDelete.size() + ' CURSOR_BUG_TEST_ accounts. Done.');
