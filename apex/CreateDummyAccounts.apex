// Apex script to create 5,000 dummy Account records
// This script will be executed via Salesforce CLI

// List to hold all accounts for bulk insert
List<Account> accountsToInsert = new List<Account>();

// Sample company names for variety
String[] companyPrefixes = new String[]{
    'Acme', 'Global', 'Tech', 'Innovation', 'Digital', 'Smart', 'Future', 'Next', 'Elite', 'Prime',
    'Advanced', 'Dynamic', 'Creative', 'Strategic', 'Professional', 'Enterprise', 'Solutions', 'Systems',
    'Technologies', 'Industries', 'Corporation', 'Inc', 'LLC', 'Partners', 'Group', 'Associates'
};

String[] companySuffixes = new String[]{
    'Corp', 'Inc', 'LLC', 'Ltd', 'Company', 'Enterprises', 'Solutions', 'Systems', 'Technologies',
    'Industries', 'Partners', 'Group', 'Associates', 'Consulting', 'Services', 'International',
    'Global', 'Worldwide', 'Network', 'Alliance'
};

String[] industries = new String[]{
    'Technology', 'Healthcare', 'Finance', 'Manufacturing', 'Retail', 'Education', 'Real Estate',
    'Transportation', 'Energy', 'Media', 'Consulting', 'Legal', 'Insurance', 'Construction',
    'Hospitality', 'Automotive', 'Pharmaceuticals', 'Telecommunications', 'Aerospace', 'Biotechnology'
};

String[] types = new String[]{
    'Customer', 'Prospect', 'Partner', 'Competitor', 'Other'
};

Integer targetRecords = 5000;
Long startTime = System.currentTimeMillis();

// Configure DML options to disable duplicate detection
Database.DMLOptions dmlOpts = new Database.DMLOptions();
dmlOpts.duplicateRuleHeader.allowSave = true;  // Allow saving even with duplicates
dmlOpts.duplicateRuleHeader.runAsCurrentUser = true;

// Create 5,000 dummy accounts in a single batch
for(Integer i = 1; i <= targetRecords; i++) {
    // Generate unique company name
    String prefix = companyPrefixes[Math.mod(i, companyPrefixes.size())];
    String suffix = companySuffixes[Math.mod(i + 5, companySuffixes.size())];
    String timestamp = String.valueOf(startTime + i);
    String uniqueId = String.valueOf(i).leftPad(5, '0');
    String companyName = 'TEST_' + prefix + '_' + suffix + '_' + uniqueId + '_' + timestamp;
    
    // Generate random industry and type
    String industry = industries[Math.mod(i, industries.size())];
    String type = types[Math.mod(i, types.size())];
    
    // Create account record
    Account acc = new Account(
        Name = companyName,
        Industry = industry,
        Type = type,
        BillingStreet = 'TEST Street ' + String.valueOf(i),
        BillingCity = 'TEST City ' + String.valueOf(Math.mod(i, 100)),
        BillingState = 'TEST State ' + String.valueOf(Math.mod(i, 50)),
        BillingPostalCode = String.valueOf(90000 + Math.mod(i, 10000)),
        BillingCountry = 'United States',
        Phone = '+1-555-' + String.valueOf(100 + Math.mod(i, 900)).leftPad(3, '0') + '-' + String.valueOf(1000 + Math.mod(i, 9000)).leftPad(4, '0'),
        Website = 'www.test' + uniqueId + timestamp + '.com',
        Description = 'TEST Dummy account created for testing purposes. Account #' + String.valueOf(i),
        AnnualRevenue = Math.random() * 10000000, // Random revenue up to 10M
        NumberOfEmployees = Math.mod(i, 1000) + 1 // 1 to 1000 employees
    );
    
    accountsToInsert.add(acc);
}

// Insert all 5,000 accounts in a single DML operation with duplicate detection disabled
try {
    Database.SaveResult[] results = Database.insert(accountsToInsert, dmlOpts);
    Integer totalCreated = 0;
    for(Database.SaveResult sr : results) {
        if(sr.isSuccess()) {
            totalCreated++;
        }
    }
    System.debug('Successfully created ' + totalCreated + ' out of ' + targetRecords + ' accounts');
    System.debug('Script execution completed successfully!');
} catch(Exception e) {
    System.debug('Error inserting accounts: ' + e.getMessage());
} 