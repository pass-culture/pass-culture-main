import type { Context } from '@sentry/browser'
import type { Extras } from '@sentry/core/build/types/types-hoist/extra.d.ts'

export type FrontendErrorOptions = Partial<{
  /** Sentry context to attach to the error. */
  context: Context
  /** Additional Sentry extras to attach to the error. */
  extras: Extras
  /**
   * Whether to notify the user about the error.
   * @default false
   */
  isSilent: boolean
  /**
   * End-user message to display (unless `isSilent` is set to `true`).
   * @default "Une erreur est survenue de notre côté. Veuillez réessayer plus tard."
   */
  userMessage: string
}>
