// scripts/report-slow-from-vitest-json.mjs
import fs from "node:fs";
import path from "node:path";

function parseArgs(argv) {
	const args = { file: null, top: 20, threshold: null, json: false, group: false };
	for (let i = 2; i < argv.length; i++) {
		const a = argv[i];
		if (!args.file && !a.startsWith("--")) args.file = a;
		else if (a === "--json") args.json = true;
		else if (a === "--group") args.group = true; // affiche aussi le ranking par fichier
		else if (a.startsWith("--top=")) args.top = Number(a.split("=")[1]);
		else if (a === "--top") args.top = Number(argv[++i]);
		else if (a.startsWith("--threshold=")) args.threshold = Number(a.split("=")[1]);
		else if (a === "--threshold") args.threshold = Number(argv[++i]);
		else {
			console.error(`Argument non reconnu: ${a}`);
			process.exit(2);
		}
	}
	if (!args.file) {
		console.error("Usage: node scripts/report-slow-from-vitest-json.mjs <report.json> [--top N] [--threshold ms] [--json] [--group]");
		process.exit(2);
	}
	return args;
}

function readJson(file) {
	const abs = file === "-" ? null : path.resolve(process.cwd(), file);
	const data = file === "-" ? fs.readFileSync(0, "utf8") : fs.readFileSync(abs, "utf8");
	return JSON.parse(data);
}

function fmt(ms) {
	const n = Number(ms);
	if (!Number.isFinite(n)) return "—";
	return `${Math.round(n)} ms`;
}

function main() {
	const { file, top, threshold, json, group } = parseArgs(process.argv);
	const rep = readJson(file);

	if (!rep || !Array.isArray(rep.testResults)) {
		console.error("Format inattendu: on attend une clé 'testResults' (tableau).");
		process.exit(1);
	}

	// 1) Flatten des assertions (tests individuels)
	const tests = [];
	for (const suite of rep.testResults) {
		const filePath = suite.name;
		const assertions = Array.isArray(suite.assertionResults) ? suite.assertionResults : [];
		for (const a of assertions) {
			const duration = Number(a.duration ?? 0);
			const title = a.fullName || a.title || "(untitled)";
			const status = a.status || "unknown";
			tests.push({ file: filePath, title, status, duration });
		}
	}

	// 2) Tri par durée décroissante + filtrage seuil éventuel
	let sorted = tests.sort((a, b) => (b.duration || 0) - (a.duration || 0));
	if (threshold != null) sorted = sorted.filter(t => (t.duration || 0) >= threshold);
	const picked = sorted.slice(0, top);

	// 3) Regroupement par fichier (somme des durations des assertions)
	const byFile = new Map();
	for (const t of tests) {
		const acc = byFile.get(t.file) || { file: t.file, total: 0, count: 0 };
		acc.total += Number(t.duration || 0);
		acc.count += 1;
		byFile.set(t.file, acc);
	}
	const files = Array.from(byFile.values()).sort((a, b) => b.total - a.total);
	const filesPicked = threshold != null
		? files // seuil non appliqué au cumul fichier, on garde l’ordre naturel
		: files;

	if (json) {
		console.log(JSON.stringify({
			meta: {
				totalSuites: rep.numTotalTestSuites,
				totalTests: rep.numTotalTests,
				threshold,
				top,
			},
			slowTests: picked,
			slowFiles: filesPicked.slice(0, top),
		}, null, 2));
		return;
	}

	// Sortie console lisible
	const header1 = ["Durée", "Statut", "Fichier", "Test"];
	const rows1 = [header1];
	for (const t of picked) {
		const flag = threshold != null && t.duration >= threshold ? "⏱️" : " ";
		const status = t.status === "passed" ? "✅ pass" : (t.status === "failed" ? "❌ fail" : t.status);
		rows1.push([`${flag} ${fmt(t.duration)}`, status, t.file, t.title]);
	}
	const widths1 = header1.map((_, i) => Math.max(...rows1.map(r => String(r[i]).length)));
	const out1 = rows1.map(r => r.map((c, i) => String(c).padEnd(widths1[i])).join("  |  ")).join("\n");

	console.log(`\nTests lents (top ${top}${threshold != null ? `, seuil ${threshold}ms` : ""})`);
	console.log("-".repeat(120));
	console.log(out1);
	console.log("-".repeat(120));

	if (group) {
		const header2 = ["Total (fichier)", "Tests", "Fichier"];
		const rows2 = [header2];
		for (const f of filesPicked.slice(0, top)) {
			rows2.push([fmt(f.total), String(f.count), f.file]);
		}
		const widths2 = header2.map((_, i) => Math.max(...rows2.map(r => String(r[i]).length)));
		const out2 = rows2.map(r => r.map((c, i) => String(c).padEnd(widths2[i])).join("  |  ")).join("\n");

		console.log(`\nFichiers les plus coûteux (somme des assertions, top ${top})`);
		console.log("-".repeat(120));
		console.log(out2);
		console.log("-".repeat(120));
	}

	console.log(`Source: ${file} • Suites: ${rep.numTotalTestSuites} • Tests: ${rep.numTotalTests}\n`);
}

main();
