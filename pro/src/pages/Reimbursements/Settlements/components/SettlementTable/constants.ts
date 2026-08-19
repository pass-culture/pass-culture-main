import { SettlementStatus } from '@/apiClient/v1'
import { TagVariant } from '@/design-system/Tag/Tag'

export const SETTLEMENT_STATUS_LABELS = {
  [SettlementStatus.ISSUED]: {
    label: 'Virement émis',
    variant: TagVariant.SUCCESS,
  },
  [SettlementStatus.EXECUTED]: {
    label: 'Virement émis',
    variant: TagVariant.SUCCESS,
  },
  [SettlementStatus.REJECTED]: {
    label: 'Rejet bancaire',
    variant: TagVariant.ERROR,
  },
} as const
