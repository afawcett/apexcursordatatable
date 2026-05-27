@IsTest
private class ReportingDrillDownControllerTest {
    @TestSetup
    static void setupObservations() {
        List<UnitPriceObservation__c> rows = new List<UnitPriceObservation__c>();
        Date start = Date.today().addDays(-59);
        for (Integer i = 0; i < 60; i++) {
            Date d = start.addDays(i);
            String dateKey = DateTime.newInstanceGmt(d.year(), d.month(), d.day(), 0, 0, 0).formatGmt('yyyy-MM-dd');
            rows.add(
                new UnitPriceObservation__c(
                    External_Id__c = 'RAM_' + dateKey,
                    Product__c = 'RAM',
                    EffectiveDate__c = d,
                    Value__c = 100 + i
                )
            );
            rows.add(
                new UnitPriceObservation__c(
                    External_Id__c = 'CPU_' + dateKey,
                    Product__c = 'CPU',
                    EffectiveDate__c = d,
                    Value__c = 200 + i
                )
            );
        }
        insert rows;
    }

    @IsTest
    static void initializeSeries_returnsMonthlyPointsFromCursor() {
        Test.startTest();
        ReportingDrillDownController.ChartSeriesResult result =
            ReportingDrillDownController.initializeSeries('RAM');
        Test.stopTest();

        System.assertEquals('RAM', result.product);
        System.assertEquals(60, result.dailyRowCount);
        System.assert(!result.monthlyPoints.isEmpty(), 'Expected monthly cursor plot points');
        System.assert(result.cursorFetchCount > 0, 'Expected fetchPage calls to build chart');
        System.assert(result.cursorFetchCount <= 100, 'Chart init should stay within fetch limit');
        System.assertNotEquals(null, Cache.Session.get('reportingDrillDownPCRAM'));
    }

    @IsTest
    static void fetchDetailRange_returnsDailyRowsForIndexRange() {
        ReportingDrillDownController.initializeSeries('RAM');

        Test.startTest();
        ReportingDrillDownController.DetailRangeResult detail =
            ReportingDrillDownController.fetchDetailRange('RAM', 2, 4);
        Test.stopTest();

        System.assertEquals(3, detail.records.size());
        System.assertEquals(2, detail.startIndex);
        System.assertEquals(4, detail.endIndex);
    }

    @IsTest
    static void refreshSeries_rebuildsSessionCursor() {
        ReportingDrillDownController.initializeSeries('CPU');
        ReportingDrillDownController.ChartSeriesResult refreshed =
            ReportingDrillDownController.refreshSeries('CPU');

        System.assertEquals(60, refreshed.dailyRowCount);
        System.assertNotEquals(null, Cache.Session.get('reportingDrillDownPCCPU'));
    }
}
