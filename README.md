# Apex Cursor Demo

Lightning demos for **Apex Cursors** (`Database.Cursor` and pagination cursors) with LWC: infinite scroll, reporting drill-down, and adaptive async chunking. Blog posts: [infinite scroll](https://andyinthecloud.com/2025/08/04/infinite-data-scrolling-with-apex-cursors-beta/) and [pagination cursors](https://andyinthecloud.com/2026/01/19/improved-infinite-data-scrolling-with-new-apex-pagination-cursors-ga/).

## 🎯 Demo Overview

| Tab | What it shows |
|-----|----------------|
| **Infinite Loading** | `Database.Cursor` + lightning-datatable infinite scroll (5,000 Accounts) |
| **Reporting Drill Down** | Pagination cursor + Chart.js brush/zoom on `UnitPriceObservation__c` |
| **Adaptive Async** | Cursor over Orders, callout-budgeted queueable chunks, `AdaptiveAsyncChunk__e` platform events |

Shared: **ApexCursorDemo** app and permission set.

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

### Step 5: Load reporting drill-down data (optional)

```bash
# Generate ~8 years of daily RAM/CPU unit prices (CSV)
node scripts/generate-price-observations.mjs

# Upsert into UnitPriceObservation__c
sf data upsert bulk \
  -f data/unit-price-observations.csv \
  -s UnitPriceObservation__c \
  -i External_Id__c \
  -o apex-cursor-demo \
  -w 10
```

### Step 6: Open the Demo

```bash
# Infinite Loading tab
sf org open --path /lightning/n/InfiniteLoading

# Reporting drill-down tab (weekly chart + cursor detail)
sf org open --path /lightning/n/ReportingDrillingDown

# Adaptive Async tab (cursor + queueable + platform events)
sf org open --path /lightning/n/AdaptiveAsync
```

### Step 7: Load Adaptive Async demo orders (required for that tab)

```bash
# Generate CSV, delete existing ADAPT-ORD-* orders, then bulk upsert accounts and orders
node scripts/generate-adaptive-orders.mjs --load
```

## 🎮 How to Use the Demo

### Infinite Loading tab

1. **Open the Demo**: The command above will take you directly to the Infinite Loading tab
2. **View the Data Table**: The component will automatically load the first batch of records
3. **Test Infinite Scrolling**: Scroll to the bottom of the table to load more records
4. **Monitor Debug Info**: Check the debug section at the bottom for real-time information

### Reporting Drilling Down tab

1. Choose **RAM** or **CPU** and wait for the monthly chart (mid-month values via pagination cursor `fetchPage`, no aggregate SOQL)
2. **Drag** across the chart to select a date range (snaps to days; drag handles to resize)
3. Daily rows for that range load below via **pagination cursor** `fetchPage` from session cache
4. Click **Refresh** to rebuild the session cursor and chart after data changes

### Adaptive Async tab

1. Open **Adaptive Async** in the Apex Cursor Demo app (1500 demo orders after Step 7; rerunnable without reset)
2. Click **Start run** — each queueable scans the next cursor window and packs orders until **`Limits.getLimitCallouts()`** predicted HTTP callouts would be exceeded
3. **Progress bar** updates as `AdaptiveAsyncChunk__e` platform events arrive
4. **Bar chart** — bar color reflects callout pressure (green / amber / red); chunk size varies with order mix
5. **Datatable** lists each chunk (sequence, planned vs actual orders, predicted callouts, job id)

