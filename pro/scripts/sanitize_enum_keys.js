/**
 * Post-processing script to sanitize generated enum keys.
 * Replaces accents, commas, and other non-ASCII characters with underscores
 * to match the output style of the previous openapi-typescript-codegen generator.
 *
 * Usage: node scripts/fix_enum_keys.js <file1> [file2] ...
 */

import { promises as fs } from 'node:fs'

// Matches an entire enum block.
const ENUM_BLOCK_RE = /^(export enum \w+ \{)([\s\S]*?)(^\})/gm

// Matches a single enum member line by its string value
const ENUM_LINE_RE = /^(\s*)[^=\n]+=\s*'([^']+)'/gm

function sanitizeEnumKey(value) {
  return value
    .replace(/[^a-zA-Z0-9_]/g, '_')
    .replace(/_+/g, '_')
    .toUpperCase()
}

async function processFile(filePath) {
  const content = await fs.readFile(filePath, 'utf-8')

  const result = content.replace(
    ENUM_BLOCK_RE,
    (_match, header, body, closing) => {
      const fixedBody = body.replace(ENUM_LINE_RE, (_m, indent, value) => {
        const key = sanitizeEnumKey(value)
        return `${indent}${key} = '${value}'`
      })
      return `${header}${fixedBody}${closing}`
    }
  )

  await fs.writeFile(filePath, result)
  console.info(`Fixed enum keys in ${filePath}`)
}

const filePaths = process.argv.slice(2)
if (filePaths.length === 0) {
  console.error('Usage: node scripts/sanitize_enum_keys.js <file1> [file2] ...')
  process.exit(1)
}

for (const filePath of filePaths) {
  await processFile(filePath)
}
