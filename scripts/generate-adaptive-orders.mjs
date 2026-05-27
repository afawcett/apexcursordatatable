#!/usr/bin/env node
/**
 * Generates 1500 demo orders in cursor order (External_Id__c).
 *
 * Chunk sizing is driven by SEGMENTS: each segment is
 *   [ (segmentLength - 100) rows @ 0 HTTP callouts ]
 *   [ 100 rows @ 1 callout (international) ]
 * so one queueable chunk consumes the whole segment (up to 320-order cap).
 *
 * Callouts (AdaptiveOrderWorkerQueueable): Digital__c → 0; USA → 0; non-USA → 1.
 *
 * Usage:
 *   node scripts/generate-adaptive-orders.mjs --load
 */
import { execSync } from 'node:child_process';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ORDER_COUNT = 1500;
const ACCOUNT_COUNT = 24;
const INTL_ROWS_PER_SEGMENT = 100;
const TARGET_ORG = process.env.SF_TARGET_ORG || 'apex-cursor-demo';
const LOAD_TO_ORG = process.argv.includes('--load');

const PRIORITIES = ['Standard', 'Standard', 'Standard', 'Gold', 'Platinum', 'Standard'];

/**
 * segmentLength = orders in one chunk; last 100 rows are international.
 * padKind: digital | domestic (0 callouts).
 */
const SEGMENTS = [
    { segmentLength: 320, padKind: 'digital', note: 'chunk 1: 220 digital + 100 intl' },
    { segmentLength: 130, padKind: 'digital', note: 'chunk 2: 30 digital + 100 intl' },
    { segmentLength: 350, padKind: 'digital', note: 'chunk 3: 250 digital + 100 intl' },
    { segmentLength: 300, padKind: 'domestic', note: 'chunk 4: 200 domestic + 100 intl' },
    { segmentLength: 400, padKind: 'digital', note: 'chunk 5: 300 digital + 100 intl' }
];

const __dirname = dirname(fileURLToPath(import.meta.url));
const rootDir = join(__dirname, '..');
const outDir = join(rootDir, 'data');
const accountFile = join(outDir, 'adaptive-accounts.csv');
const orderFile = join(outDir, 'adaptive-orders.csv');
const clearApexFile = join(rootDir, 'apex', 'ClearAdaptiveOrders.apex');

function profileForKind(kind) {
    if (kind === 'digital') {
        return {
            country: 'USA',
            payment: 'Paid',
            hazmat: false,
            expedited: false,
            digital: true
        };
    }
    if (kind === 'domestic') {
        return {
            country: 'USA',
            payment: 'Paid',
            hazmat: false,
            expedited: false,
            digital: false
        };
    }
    return {
        country: 'DEU',
        payment: 'Paid',
        hazmat: true,
        expedited: false,
        digital: false
    };
}

function buildOrderRows() {
    const rows = [];
    let orderIndex = 0;

    for (const segment of SEGMENTS) {
        const padCount = segment.segmentLength - INTL_ROWS_PER_SEGMENT;
        if (padCount < 0) {
            throw new Error(
                `segmentLength ${segment.segmentLength} must be >= ${INTL_ROWS_PER_SEGMENT}`
            );
        }

        for (let i = 0; i < padCount; i++) {
            orderIndex += 1;
            rows.push(formatRow(orderIndex, profileForKind(segment.padKind)));
        }
        for (let i = 0; i < INTL_ROWS_PER_SEGMENT; i++) {
            orderIndex += 1;
            rows.push(formatRow(orderIndex, profileForKind('international')));
        }
    }

    if (orderIndex !== ORDER_COUNT) {
        throw new Error(`Expected ${ORDER_COUNT} orders, built ${orderIndex}`);
    }

    return rows;
}

function formatRow(orderIndex, profile) {
    const orderId = `ADAPT-ORD-${String(orderIndex).padStart(5, '0')}`;
    const accountId = `ADAPT-ACCT-${String((orderIndex % ACCOUNT_COUNT) + 1).padStart(4, '0')}`;
    const amount = (75 + (orderIndex % 50) * 80).toFixed(2);
    const today = new Date().toISOString().slice(0, 10);
    return [
        orderId,
        accountId,
        today,
        'Draft',
        profile.country,
        profile.payment,
        profile.hazmat,
        profile.expedited,
        amount,
        profile.digital
    ].join(',');
}

function runSf(command) {
    execSync(command, { cwd: rootDir, stdio: 'inherit', encoding: 'utf8' });
}

function clearDemoOrders() {
    console.log(`Clearing ADAPT-ORD-* orders in org ${TARGET_ORG}...`);
    runSf(`sf apex run --file "${clearApexFile}" -o ${TARGET_ORG}`);
}

function loadCsvToOrg() {
    clearDemoOrders();
    console.log('Upserting accounts...');
    runSf(
        `sf data upsert bulk -o ${TARGET_ORG} -s Account -f "${accountFile}" -i External_Id__c -w 10`
    );
    console.log('Upserting orders...');
    runSf(
        `sf data upsert bulk -o ${TARGET_ORG} -s Order -f "${orderFile}" -i External_Id__c -w 20`
    );
}

async function main() {
    await mkdir(outDir, { recursive: true });

    const accountRows = [
        'External_Id__c,Name,CustomerPriority__c',
        ...Array.from({ length: ACCOUNT_COUNT }, (_, i) => {
            const id = `ADAPT-ACCT-${String(i + 1).padStart(4, '0')}`;
            const priority = PRIORITIES[i % PRIORITIES.length];
            return `${id},Adaptive Customer ${i + 1},${priority}`;
        })
    ];

    const orderRows = [
        'External_Id__c,Account.External_Id__c,EffectiveDate,Status,Shipping_Country__c,Payment_Status__c,Contains_Hazmat__c,Expedited__c,Order_Amount__c,Digital__c',
        ...buildOrderRows()
    ];

    await writeFile(accountFile, accountRows.join('\n'));
    await writeFile(orderFile, orderRows.join('\n'));
    console.log(`Wrote ${ORDER_COUNT} orders — ${SEGMENTS.length} segments (100 intl at end of each)`);
    for (const segment of SEGMENTS) {
        console.log(`  length ${segment.segmentLength} (${segment.note})`);
    }

    if (LOAD_TO_ORG) {
        loadCsvToOrg();
        console.log(`Loaded demo data into org ${TARGET_ORG}.`);
    } else {
        console.log('CSV only. Load: node scripts/generate-adaptive-orders.mjs --load');
    }
}

main().catch((err) => {
    console.error(err);
    process.exit(1);
});
