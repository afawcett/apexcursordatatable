#!/usr/bin/env node
/**
 * Subscribes to AdaptiveAsyncChunk__e and prints telemetry payloads.
 * Auth from: sf org display --json (accessToken + instanceUrl).
 *
 * Usage:
 *   node scripts/listen-adaptive-chunk-events.mjs
 *   node scripts/listen-adaptive-chunk-events.mjs --run-probe
 */
import { execSync, spawnSync } from 'node:child_process';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import jsforce from 'jsforce';

const TARGET_ORG = process.env.SF_TARGET_ORG || 'apex-cursor-demo';
const CHANNEL = '/event/AdaptiveAsyncChunk__e';
const RUN_PROBE = process.argv.includes('--run-probe');

const __dirname = dirname(fileURLToPath(import.meta.url));
const rootDir = join(__dirname, '..');

function getOrg() {
    const raw = execSync(`sf org display --target-org ${TARGET_ORG} --json`, {
        encoding: 'utf8'
    });
    const parsed = JSON.parse(raw);
    if (parsed.status !== 0 || !parsed.result) {
        throw new Error(`Could not read org ${TARGET_ORG}: ${raw}`);
    }
    return parsed.result;
}

function startProbe() {
    const probeFile = join(rootDir, '.tmp', 'RunAdaptiveRuntimeProbe.apex');
    const result = spawnSync(
        'sf',
        ['apex', 'run', '--file', probeFile, '-o', TARGET_ORG],
        { encoding: 'utf8' }
    );
    if (result.status !== 0) {
        console.error(result.stderr || result.stdout);
        throw new Error('Probe apex run failed');
    }
    const match = (result.stdout || '').match(/runId=([A-Za-z0-9]+)/);
    if (match) {
        console.log(`Started probe runId=${match[1]}`);
    }
    return result.stdout;
}

async function main() {
    const org = getOrg();
    const conn = new jsforce.Connection({
        instanceUrl: org.instanceUrl,
        accessToken: org.accessToken,
        version: org.apiVersion || '66.0'
    });

    const events = [];

    console.log(`Org: ${org.username}`);
    console.log(`Subscribing to ${CHANNEL} ...`);

    const fayeClient = conn.streaming.createClient();

    await new Promise((resolve, reject) => {
        const subscription = fayeClient.subscribe(CHANNEL, (message) => {
            const payload = message?.payload ?? message;
            events.push(payload);
            console.log('\n--- AdaptiveAsyncChunk__e ---');
            console.log(JSON.stringify(payload, null, 2));
        });

        subscription.callback(() => {
            console.log('Subscribed.');
            if (RUN_PROBE) {
                setTimeout(() => startProbe(), 500);
                setTimeout(() => {
                    subscription.cancel();
                    resolve();
                }, 30000);
            } else {
                console.log('Waiting for events (Ctrl+C to exit). Pass --run-probe to enqueue probe.');
            }
        });

        subscription.errback((err) => reject(err));
    });

    if (RUN_PROBE) {
        console.log(`\nReceived ${events.length} event(s).`);
        if (events.length < 4) {
            process.exitCode = 1;
        }
    }
}

main().catch((err) => {
    console.error(err);
    process.exit(1);
});
