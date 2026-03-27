/**
 * Formats auto-generated index.ts files from @hey-api/openapi-ts.
 *
 * Splits inline re-export statements into sorted, one-per-line exports
 * to reduce git merge conflicts and improve readability.
 *
 * Usage: node scripts/formatGeneratedIndexExports.js <file1> [file2] ...
 */

import { promises as fs } from 'node:fs'

const EXPORT_RE = /^export\s*\{([^}]+)\}\s*from\s*('[^']+'|"[^"]+");?\s*$/

/**
 * Extracts the sort key from a specifier (the identifier name, ignoring `type` prefix).
 */
function getSortKey(specifier) {
  return specifier.replace(/^type\s+/, '')
}

/**
 * Parses and reformats a single export line into sorted, multi-line format.
 */
function formatExportLine(line) {
  const match = line.match(EXPORT_RE)
  if (!match) {
    return line
  }

  const specifiers = match[1]
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean)
    .sort((a, b) => {
      const keyA = getSortKey(a)
      const keyB = getSortKey(b)

      if (keyA < keyB) {
        return -1
      }
      if (keyA > keyB) {
        return 1
      }

      const aIsType = a.startsWith('type ')
      const bIsType = b.startsWith('type ')

      return Number(aIsType) - Number(bIsType)
    })

  const source = match[2]
  const specifierLines = specifiers.map((s) => `  ${s},`).join('\n')

  return `export {\n${specifierLines}\n} from ${source}`
}

async function formatFile(filePath) {
  const content = await fs.readFile(filePath, 'utf-8')
  const lines = content.split('\n')
  const formattedLines = lines.map((line) => formatExportLine(line))
  const formatted = formattedLines.join('\n')

  if (formatted !== content) {
    await fs.writeFile(filePath, formatted)
    console.info(`Formatted: ${filePath}`)
  } else {
    console.info(`Already formatted: ${filePath}`)
  }
}

const filePaths = process.argv.slice(2)
if (filePaths.length === 0) {
  console.error(
    'Usage: node scripts/formatGeneratedIndexExports.js <file1> [file2] ...'
  )
  process.exit(1)
}

for (const filePath of filePaths) {
  await formatFile(filePath)
}
