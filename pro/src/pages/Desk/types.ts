import { type EnumType } from 'commons/custom_types/utils'

export const MESSAGE_VARIANT = {
  DEFAULT: 'default',
  ERROR: 'error',
  SUCCESS: 'success',
} as const
// eslint-disable-next-line no-redeclare, @typescript-eslint/naming-convention
export type MESSAGE_VARIANT = EnumType<typeof MESSAGE_VARIANT>

export interface ErrorMessage {
  message: string
  variant: MESSAGE_VARIANT
}
