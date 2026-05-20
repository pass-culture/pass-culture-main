/**
 * Path roots and conversions shared by every utility.
 *
 * `PROJECT_ROOT` is the `pro/` directory regardless of where the script is
 * invoked from; downstream code uses it to resolve `@/...` imports, glob
 * patterns, and the display path in reports.
 */

import { posix, relative, resolve, sep } from 'node:path'

export const PROJECT_ROOT = resolve(import.meta.dirname, '..', '..', '..')
export const SRC_ROOT = resolve(PROJECT_ROOT, 'src')

/**
 * Converts a platform-specific path to forward-slash form, suitable for
 * display and glob matching.
 */
export function toPosixPath(value) {
  return value.split(sep).join(posix.sep)
}

/**
 * Returns the given absolute path made relative to `PROJECT_ROOT` and
 * normalized to forward slashes.
 */
export function formatLocation(filePath) {
  return toPosixPath(relative(PROJECT_ROOT, filePath))
}
