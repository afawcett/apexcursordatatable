# Apex Cursor Demo with Lightning Data Table Infinite Scrolling

This project demonstrates the new beta Apex Cursors feature working with Lightning Web Components and the Lightning Data Table's infinite scrolling capability. You can read more about this in my blog [here](https://andyinthecloud.com/2025/08/04/infinite-data-scrolling-with-apex-cursors-beta/) and [here](https://andyinthecloud.com/2026/01/19/improved-infinite-data-scrolling-with-new-apex-pagination-cursors-ga/).

## 🎯 Demo Overview

- **Apex Cursors**: Uses the new beta `Database.Cursor` API for efficient pagination
- **Lightning Data Table**: Implements infinite scrolling with `enable-infinite-loading`
- **5,000 Test Records**: Pre-populated Account records for testing
- **Permission Set**: Complete access control setup

## 📋 Prerequisites

- Salesforce CLI (`sf`) installed and authenticated
- A Dev Hub org configured
- Basic knowledge of Lightning Web Components and Apex

## 🚀 Setup Instructions

### Step 1: Create a New Scratch Org

```bash
# Create a fresh scratch org
sf org create scratch --definition-file config/project-scratch-def.json --alias apex-cursor-demo --set-default --duration-days 7
```

### Step 2: Deploy the Project Metadata

```bash
# Deploy all metadata to the scratch org
sf project deploy start
```

### Step 3: Create Test Data (5,000 Account Records)

```bash
# Run the Apex script to create dummy Account records
sf apex run --file apex/CreateDummyAccounts.apex
```

### Step 4: Assign Permission Set

```bash
# Assign the permission set
sf org assign permset --name ApexCursorDemo
```

### Step 5: Open the Demo

```bash
# Open the org directly to the Infinite Loading tab
sf org open --path /lightning/n/InfiniteLoading
```

## 🎮 How to Use the Demo

1. **Open the Demo**: The command above will take you directly to the Infinite Loading tab
2. **View the Data Table**: The component will automatically load the first batch of records
3. **Test Infinite Scrolling**: Scroll to the bottom of the table to load more records
4. **Monitor Debug Info**: Check the debug section at the bottom for real-time information

## 📁 Project Structure

```
apexcursordatatable/
├── apex/
│   └── CreateDummyAccounts.apex          # Script to create test data
├── config/
│   └── project-scratch-def.json          # Scratch org definition
├── force-app/main/default/
│   ├── applications/
│   │   └── ApexCursorDemo.app-meta.xml   # Custom Lightning app
│   ├── classes/
│   │   └── ApexCursorDemoController.cls  # Apex controller with cursor logic
│   ├── lwc/
│   │   └── apexCursorDemo/               # Lightning Web Component
│   │       ├── apexCursorDemo.html       # Component template
│   │       ├── apexCursorDemo.js         # Component logic
│   │       └── apexCursorDemo.js-meta.xml
│   ├── permissionsets/
│   │   └── ApexCursorDemo.permissionset-meta.xml  # Permission set
│   └── tabs/
│       └── InfiniteLoading.tab-meta.xml  # Custom tab
└── README.md
```

## 🔧 Key Components

### ApexCursorDemoController.cls
- **`loadMoreRecords()`**: Main method using Apex Cursors
- **Cursor Management**: Handles `Database.Cursor` creation and pagination
- **Error Handling**: Robust error handling for cursor operations

### apexCursorDemo (LWC)
- **Infinite Scrolling**: Uses `enable-infinite-loading` and `onloadmore`
- **Data Binding**: Reactive data properties for real-time updates
- **Error Display**: User-friendly error messages

### Permission Set
- **App Access**: Access to "Apex Cursor Demo" application
- **Tab Access**: Access to "Infinite Loading" tab
- **Object Permissions**: Full Account object access
- **Apex Access**: Access to controller class

## 🧪 Testing the Demo

### Expected Behavior
1. **Initial Load**: Should display first 50 Account records
2. **Infinite Scroll**: Scrolling to bottom loads next 50 records
3. **Performance**: Smooth loading without page refreshes
4. **Debug Info**: Shows loaded records count, total records, and has more status

### Troubleshooting
- **No Data**: Ensure the Apex script ran successfully
- **Permission Errors**: Verify permission set assignment
- **Component Not Loading**: Check browser console for JavaScript errors

## 🧹 Cleanup

```bash
# Delete the scratch org when done testing
sf org delete scratch --target-org apex-cursor-demo
```

## Pagination Cursor behavior tests

This section describes the investigation and Apex tests in `PaginationCursorBugTest.cls`, motivated by [blog comments](https://andyinthecloud.com/2026/01/19/improved-infinite-data-scrolling-with-new-apex-pagination-cursors-ga/) on partial last pages and records deleted while a cursor is in use.

### Why we ran these tests

Community feedback reported that `PaginationCursor.fetchPage(start, pageSize)` throws when `(start + pageSize)` exceeds `getNumRecords()`—for example, with 5,003 records and page size 50, the last 3 records are never returned. The [Apex Cursors documentation](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_cursors.htm) describes skipping deleted rows and returning a partial final page when the cursor reaches the end before `pageSize`. We wanted to see whether the platform matches that documentation or enforces a strict bound that callers must satisfy.

### What we tested

Tests use **53 Account records** and **page size 50** so the last page has only 3 rows. Each scenario has two methods side by side: one uses raw `PAGE_SIZE` for the last fetch; the variant caps the request with `Math.min(PAGE_SIZE, cursor.getNumRecords() - start)`.

| Scenario | Without cap (expects doc behavior) | With cap (DX workaround) |
|----------|-----------------------------------|---------------------------|
| **Partial last page** | `fetchPagePartialLastPageReturnsRemainingRecordsPerDocs` — `fetchPage(50, 50)` | `fetchPagePartialLastPageReturnsRemainingRecordsPerDocsVariant` — `fetchPage(50, 3)` |
| **After deletes** | `fetchPageAfterRecordsDeletedSkipsDeletedAndReturnsPagePerDocs` — first 10 rows deleted, then `fetchPage(50, 50)` | `fetchPageAfterRecordsDeletedSkipsDeletedAndReturnsPagePerDocsVariant` — same setup, capped page size |

There is also a standalone script `apex/ReproducePaginationCursorBug.apex` that reproduces the throw in anonymous Apex.

### Results

| Test | Outcome | Notes |
|------|---------|--------|
| Partial last page (uncapped) | **Fail** | `InvalidParameterValueException: Fetch beyond bound detected: 100` |
| Partial last page (variant) | **Pass** | Capped `fetchPage(50, 3)` returns 3 records |
| After deletes (uncapped) | **Fail** | Same exception |
| After deletes (variant) | **Pass** | Capped `fetchPage(50, 3)` returns 3 records |

**Interpretation:** The platform requires `start + pageSize <= getNumRecords()`. It does not return a partial or empty final page when that inequality would be violated; it throws instead. The documentation example (`fetchPage(0, 20)` after deleting rows 0–4) stays within bounds because `0 + 20 <= 100`. Callers who need the last few rows must cap page size themselves:

```apex
Integer pageSizeForLastPage = Math.min(pageSize, cursor.getNumRecords() - start);
cursor.fetchPage(start, pageSizeForLastPage);
```

Whether that is a product bug or a documentation/DX gap is a matter for Salesforce; these tests document current behavior and a working workaround.

### Run the tests

```bash
sf project deploy start
sf apex run test -n PaginationCursorBugTest -l RunSpecifiedTests -r human -w 10
```


