#!/usr/bin/env node
/**
 * Generates daily unit price observations (RAM, CPU) for 8 years.
 * Prices use overlapping cycles, mean reversion, and occasional shocks
 * so series have clear peaks and lows without a steady downward drift.
 * Output: data/unit-price-observations.csv for sf data import bulk.
 */
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const PRODUCTS = [
    { name: 'RAM', base: 85, volatility: 2.2, phase: 0.4 },
    { name: 'CPU', base: 220, volatility: 4.5, phase: 1.8 }
];

const __dirname = dirname(fileURLToPath(import.meta.url));
const rootDir = join(__dirname, '..');
const outDir = join(rootDir, 'data');
const outFile = join(outDir, 'unit-price-observations.csv');

function addDays(date, days) {
    const d = new Date(date);
    d.setUTCDate(d.getUTCDate() + days);
    return d;
}

function formatDate(date) {
    return date.toISOString().slice(0, 10);
}

function daysBetween(start, end) {
    const ms = end.getTime() - start.getTime();
    return Math.round(ms / 86400000);
}

function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
}

/**
 * @param {typeof PRODUCTS[0]} product
 */
function generateSeries(product, startDate, endDate) {
    const rows = [];
    const totalDays = daysBetween(startDate, endDate) + 1;
    let price = product.base;
    let momentum = 0;

    for (let i = 0; i < totalDays; i++) {
        const effectiveDate = addDays(startDate, i);
        const t = i + product.phase * 100;

        const annual = Math.sin((t / 365) * Math.PI * 2) * product.base * 0.14;
        const semiAnnual = Math.sin((t / 182) * Math.PI * 2) * product.base * 0.07;
        const quarterly = Math.sin((t / 91) * Math.PI * 2) * product.base * 0.05;
        const monthly = Math.sin((t / 30) * Math.PI * 2) * product.base * 0.03;

        const target = product.base + annual + semiAnnual + quarterly;
        const pull = (target - price) * 0.06;

        let shock = 0;
        if (Math.random() < 0.012) {
            const sign = Math.random() > 0.5 ? 1 : -1;
            shock = sign * product.base * (0.04 + Math.random() * 0.12);
        }

        const noise = (Math.random() - 0.5) * product.volatility;
        momentum = momentum * 0.82 + noise * 0.35;
        price += pull + momentum + monthly * 0.08 + shock;

        const floor = product.base * 0.55;
        const ceiling = product.base * 1.7;
        price = clamp(price, floor, ceiling);

        const dateStr = formatDate(effectiveDate);
        rows.push({
            External_Id__c: `${product.name}_${dateStr}`,
            Product__c: product.name,
            EffectiveDate__c: dateStr,
            Value__c: price.toFixed(2)
        });
    }
    return rows;
}

async function main() {
    const endDate = new Date();
    endDate.setUTCHours(0, 0, 0, 0);
    const startDate = new Date(endDate);
    startDate.setUTCFullYear(startDate.getUTCFullYear() - 8);
    startDate.setUTCHours(0, 0, 0, 0);

    const allRows = [];
    for (const product of PRODUCTS) {
        allRows.push(...generateSeries(product, startDate, endDate));
    }

    const header = 'External_Id__c,Product__c,EffectiveDate__c,Value__c';
    const lines = allRows.map(
        (r) => `${r.External_Id__c},${r.Product__c},${r.EffectiveDate__c},${r.Value__c}`
    );
    await mkdir(outDir, { recursive: true });
    await writeFile(outFile, [header, ...lines].join('\n'), 'utf8');

    const manifest = {
        startDate: formatDate(startDate),
        endDate: formatDate(endDate),
        rowCount: allRows.length,
        products: PRODUCTS.map((p) => p.name)
    };
    await writeFile(join(outDir, 'manifest.json'), JSON.stringify(manifest, null, 2), 'utf8');

    console.log(`Wrote ${allRows.length} rows to ${outFile}`);
    console.log(`Date range: ${manifest.startDate} .. ${manifest.endDate}`);
}

main().catch((err) => {
    console.error(err);
    process.exit(1);
});
