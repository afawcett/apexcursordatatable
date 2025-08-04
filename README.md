# Apex Cursor Demo with Lightning Data Table Infinite Scrolling

This project demonstrates the new beta Apex Cursors feature working with Lightning Web Components and the Lightning Data Table's infinite scrolling capability.

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


