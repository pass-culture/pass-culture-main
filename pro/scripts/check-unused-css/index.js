/**
 * Lightweight in-repo replacement for the `check-unused-css` npm package.
 *
 * @description
 * Reports two issue categories for `*.module.{scss,css,sass}` files consumed by TS / TSX / JS / JSX sources under `src/`:
 *   - unused-class         A class is declared in the module but never referenced.
 *   - non-existent-class   A `styles.foo` reference targets a class that does not exist in the imported module.
 *
 * Drop-in semantics with the upstream tool:
 *   - relative imports and the `@/...` / bare `*` path aliases are honored (mirrors `pro/tsconfig.json` -> `paths`);
 *   - the same disable-comment syntax is recognized:
 *       SCSS  /* check-unused-css-disable *\/
 *             /* check-unused-css-disable-next-line *\/
 *       TS    // check-unused-css-disable
 *             // check-unused-css-disable-next-line
 *             {/* check-unused-css-disable-next-line *\/}
 *   - dynamic accesses (`styles[expr]`) skip both checks for the corresponding `(source, module)` pair.
 *
 * @example
 * ```
 * node scripts/check-unused-css [<path>] [--exclude <glob>...]
 * ```
 *
 * Default path: src
 */

import { availableParallelism } from 'node:os'

import { collectFiles } from './utils/collectFiles.js'
import { crossReference } from './utils/crossReference.js'
import { parseArgs } from './utils/parseArgs.js'
import { parseModuleFile } from './utils/parseModuleFile.js'
import { parseSourceFile } from './utils/parseSourceFile.js'
import { printResults } from './utils/printResults.js'
import { runWithConcurrency } from './utils/runWithConcurrency.js'

async function main() {
  const args = parseArgs(process.argv.slice(2))
  const startedAt = process.hrtime.bigint()

  const { modulePaths, sourcePaths } = await collectFiles(
    args.paths,
    args.excludes
  )
  const concurrency = Math.max(4, availableParallelism())

  const [moduleReports, sourceReports] = await Promise.all([
    runWithConcurrency(modulePaths, parseModuleFile, concurrency),
    runWithConcurrency(sourcePaths, parseSourceFile, concurrency),
  ])

  const result = crossReference(moduleReports, sourceReports)

  const endedAt = process.hrtime.bigint()
  const durationMs = Number(endedAt - startedAt) / 1_000_000

  const exitCode = printResults({
    ...result,
    moduleCount: moduleReports.length,
    sourceCount: sourceReports.length,
    durationMs,
  })

  process.exit(exitCode)
}

main().catch((error) => {
  console.error(error)

  process.exit(2)
})
