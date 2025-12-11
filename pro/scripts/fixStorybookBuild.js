/**
 * Fix for Storybook CSS nesting bug in production builds.
 *
 * Storybook's internal CSS in `node_modules/storybook/assets/server/base-preview-head.html`
 * uses CSS nesting syntax (& selectors) and get injected in `docs-build/iframe.html`.
 * They are incorrectly transformed during Vite production builds,
 * leaving orphaned selectors like "& h1 {...}" at root level.
 * Chrome interprets these orphaned selectors as global rules, causing unintended
 * side effects on story content (e.g., "& li + li" adds padding to all lists).
 *
 * This script removes the orphaned selectors from the built iframe.html as a workaround.
 *
 * TODO (igabriele, 2025-12-11): I will open a PR on the original Storybook repo to fix this issue.
 */

import { promises as fs } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

const IFRAME_PATH = join(__dirname, '../docs-build/iframe.html')

const ORPHANED_SELECTORS = [
  /& h1\{[^}]*\}/g,
  /& ol,& p\{[^}]*\}/g,
  /& li\+li\{[^}]*\}/g,
  /& a\{[^}]*\}/g,
]

const fixStorybookCssNesting = async () => {
  try {
    await fs.access(IFRAME_PATH)
  } catch {
    console.error(
      'error =>',
      `${IFRAME_PATH} not found. Run \`yarn build-storybook\` first.`
    )
    process.exit(1)
  }

  let content = await fs.readFile(IFRAME_PATH, 'utf-8')
  const originalLength = content.length

  for (const pattern of ORPHANED_SELECTORS) {
    content = content.replace(pattern, '')
  }

  await fs.writeFile(IFRAME_PATH, content)
  console.info(
    'info =>',
    `Fixed Storybook CSS nesting issue. Removed ${originalLength - content.length} bytes of orphaned selectors.`
  )
}

fixStorybookCssNesting()
