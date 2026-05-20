/**
 * Discovers `.module.{scss,css,sass}` and `.{ts,tsx,js,jsx}` files under each
 * root path, honoring user-supplied glob excludes.
 *
 * Excludes are passed straight to Node's `fs.promises.glob` and are matched
 * relative to the scanned root.
 */

import { glob } from 'node:fs/promises'
import { isAbsolute, resolve } from 'node:path'

import { PROJECT_ROOT } from './paths.js'

const MODULE_EXTENSIONS = ['.module.scss', '.module.css', '.module.sass']
const SOURCE_EXTENSIONS = ['.ts', '.tsx', '.js', '.jsx']

function isModuleFile(filePath) {
  return MODULE_EXTENSIONS.some((extension) => filePath.endsWith(extension))
}

function isSourceFile(filePath) {
  return SOURCE_EXTENSIONS.some((extension) => filePath.endsWith(extension))
}

/**
 * Walks every root path and returns absolute paths split into the two
 * categories the rest of the tool cares about.
 */
export async function collectFiles(rootPaths, excludes) {
  const modulePaths = []
  const sourcePaths = []
  for (const rootPath of rootPaths) {
    const absoluteRoot = isAbsolute(rootPath)
      ? rootPath
      : resolve(PROJECT_ROOT, rootPath)
    const iterator = glob('**/*', {
      cwd: absoluteRoot,
      withFileTypes: false,
      exclude: excludes,
    })
    for await (const entry of iterator) {
      const absolutePath = resolve(absoluteRoot, entry)
      if (isModuleFile(absolutePath)) modulePaths.push(absolutePath)
      else if (isSourceFile(absolutePath)) sourcePaths.push(absolutePath)
    }
  }
  return { modulePaths, sourcePaths }
}
