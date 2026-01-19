// Create a standard cursor
Database.Cursor cursor = Database.getCursor('SELECT Id, Name FROM Account LIMIT 20');
System.debug('Standard Cursors: ' + Limits.getApexCursors() + '/' + Limits.getLimitApexCursors());
System.debug('Standard Cursor Rows: ' + Limits.getApexCursorRows() + '/' + Limits.getLimitApexCursorRows());

// Fetch records
List<Account> batch1 = cursor.fetch(0, 10);
List<Account> batch2 = cursor.fetch(10, 10);

// Create a pagination cursor
Database.PaginationCursor pagCursor = Database.getPaginationCursor('SELECT Id, Name FROM Account LIMIT 15');
System.debug('Pagination Cursors: ' + Limits.getApexPaginationCursors() + '/' + Limits.getLimitApexPaginationCursors());
System.debug('Pagination Cursor Rows: ' + Limits.getApexPaginationCursorRows() + '/' + Limits.getLimitApexPaginationCursorRows());

// Fetch a page
Database.CursorFetchResult page = pagCursor.fetchPage(0, 5);

// Check shared fetch call limit
System.debug('Fetch Calls: ' + Limits.getFetchCallsOnApexCursor() + '/' + Limits.getLimitFetchCallsOnApexCursor());

// Get daily limits map
Map<String, System.OrgLimit> limitMap = OrgLimits.getMap();

// Standard cursor daily limit
System.OrgLimit dailyCursorLimit = limitMap.get('DailyApexCursorLimit');
System.debug('Daily Cursors: ' + dailyCursorLimit.getValue() + '/' + dailyCursorLimit.getLimit());

// Pagination cursor daily limit
System.OrgLimit dailyPCursorLimit = limitMap.get('DailyApexPCursorLimit');
System.debug('Daily Pagination Cursors: ' + dailyPCursorLimit.getValue() + '/' + dailyPCursorLimit.getLimit());

// Shared daily rows limit
System.OrgLimit dailyRowsLimit = limitMap.get('DailyApexCursorRowsLimit');
System.debug('Daily Cursor Rows: ' + dailyRowsLimit.getValue() + '/' + dailyRowsLimit.getLimit());