import { type EnumType } from 'commons/custom_types/utils'

export const REIMBURSEMENT_RULES = {
  STANDARD: 'STANDARD',
  NOT_REIMBURSED: 'NOT_REIMBURSED',
  BOOK: 'BOOK',
} as const
// eslint-disable-next-line no-redeclare, @typescript-eslint/naming-convention
type REIMBURSEMENT_RULES = EnumType<typeof REIMBURSEMENT_RULES>
