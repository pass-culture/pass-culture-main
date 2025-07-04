#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const __dirname = path.dirname(new URL(import.meta.url).pathname);

const E2E_DIR = path.join(__dirname, '../cypress/e2e');
const TIMINGS_PATH = process.argv[2] || './cypress-timings/results.json';
const CHUNKS = parseInt(process.env.CHUNKS, 10) || 4;
const DEFAULT_DURATION = 10; // seconds

// 1. Lister tous les fichiers de test
const allSpecs = fs.readdirSync(E2E_DIR)
  .filter(f => f.endsWith('.cy.ts'))
  .map(f => path.join('cypress/e2e', f));

// 2. Charger les timings si dispo
let timings = {};
if (fs.existsSync(TIMINGS_PATH)) {
  try {
    const data = JSON.parse(fs.readFileSync(TIMINGS_PATH, 'utf8'));
    // Cypress JSON reporter: data.results[]
    if (data && data.results) {
      data.results.forEach(res => {
        if (res.file && typeof res.duration === 'number') {
          // duration en ms, on convertit en secondes
          timings[path.basename(res.file)] = res.duration / 1000;
        }
      });
    }
  } catch (e) {
    // ignore, fallback to default
  }
}

// 3. Associer chaque spec à sa durée
const specsWithDurations = allSpecs.map(spec => {
  const base = path.basename(spec);
  return {
    spec,
    duration: timings[base] || DEFAULT_DURATION,
  };
});

// 4. Bin packing greedy (on trie par durée décroissante, on remplit les chunks les moins chargés)
const chunks = Array.from({ length: CHUNKS }, () => ({ specs: [], total: 0 }));
specsWithDurations
  .sort((a, b) => b.duration - a.duration)
  .forEach(({ spec, duration }) => {
    // Trouver le chunk le moins chargé
    const minChunk = chunks.reduce((min, c, i) => c.total < chunks[min].total ? i : min, 0);
    chunks[minChunk].specs.push(spec);
    chunks[minChunk].total += duration;
  });

// 5. Format de sortie attendu par le workflow : ["spec1,spec2", "spec3,spec4", ...]
const output = chunks.map(c => c.specs.join(','));
console.log(JSON.stringify(output)); 