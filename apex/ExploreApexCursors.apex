
Database.Cursor cursor = Database.getCursor('SELECT Id, Name, Industry, Type, BillingCity, Phone FROM Account WHERE Name LIKE \'TEST%\' WITH USER_MODE ORDER BY Name');
System.debug('***** BEFORE FETCH *****');
System.debug('Total Records: ' + cursor.getNumRecords());
System.debug('Limit Queries: ' + Limits.getLimitQueries());
System.debug('Limit Query Rows: ' + Limits.getLimitQueryRows());
System.debug('Limit Aggregate Queries: ' + Limits.getLimitAggregateQueries());
System.debug('Limit Apex Cursor Rows: ' + Limits.getLimitApexCursorRows());
System.debug('Limit Fetch Calls On Apex Cursor: ' + Limits.getLimitFetchCallsOnApexCursor());
List<Account> accounts = cursor.fetch(1, 500);
System.debug('***** AFTER FETCH *****');
System.debug('Accounts Read: ' + accounts.size());
System.debug('Limit Queries: ' + Limits.getLimitQueries());
System.debug('Limit Query Rows: ' + Limits.getLimitQueryRows());
System.debug('Limit Aggregate Queries: ' + Limits.getLimitAggregateQueries());
System.debug('Limit Apex Cursor Rows: ' + Limits.getLimitApexCursorRows());
System.debug('Limit Fetch Calls On Apex Cursor: ' + Limits.getLimitFetchCallsOnApexCursor());


