import { type EnumType } from 'commons/custom_types/utils'

export const CalloutVariant = {
  INFO: 'info',
  SUCCESS: 'success',
  WARNING: 'warning',
  ERROR: 'error',
} as const
// eslint-disable-next-line no-redeclare
export type CalloutVariant = EnumType<typeof CalloutVariant>
