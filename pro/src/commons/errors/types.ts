import type { Context } from '@sentry/browser'

export type FrontendErrorOptions = Partial<{
  /** Sentry context to attach to the error. */
  context: Context
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
