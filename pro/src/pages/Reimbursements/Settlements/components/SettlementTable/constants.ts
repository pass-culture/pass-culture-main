import { SettlementDisplayedStatus } from '@/apiClient/v1'
import { TagVariant } from '@/design-system/Tag/Tag'

export const SETTLEMENT_STATUS_LABELS = {
  [SettlementDisplayedStatus.EXECUTED]: {
    label: 'Virement émis',
    variant: TagVariant.SUCCESS,
  },
  [SettlementDisplayedStatus.REJECTED]: {
    label: 'Rejet bancaire',
    variant: TagVariant.ERROR,
  },
  [SettlementDisplayedStatus.REJECTED_PROCESSED]: {
    label: 'Rejet bancaire traité',
    variant: TagVariant.DEFAULT,
  },
  [SettlementDisplayedStatus.REJECTED_SOLVED]: {
    label: 'Rejet bancaire résolu',
    variant: TagVariant.DEFAULT,
  },
} as const
