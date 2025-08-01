import { FrontendError } from './FrontendError'
import { handleUnexpectedError } from './handleUnexpectedError'
import type { FrontendErrorOptions } from './types'

/**
 * Asserts that a condition is true in a TypeScript-friendly way,
 * throwing a gracefully handled error if the condition is false.
 *
 * @example
 * ```ts
 * const foundItem = items.find((item) => item.id === selectedItemId)
 * assertOrFrontendError(foundItem, `selectedItemId = ${selectedItemId} doesn't exist in items.`)
 * // `foundItem` is now guaranteed to be defined and TS understands it.
 * ```
 */
export function assertOrFrontendError(
  condition: any,
  errorInternalMessage: string,
  errorOptions?: FrontendErrorOptions
): asserts condition {
  if (condition) {
    return
  }

  const error = new FrontendError(errorInternalMessage)

  handleUnexpectedError(error, errorOptions)

  throw error
}
