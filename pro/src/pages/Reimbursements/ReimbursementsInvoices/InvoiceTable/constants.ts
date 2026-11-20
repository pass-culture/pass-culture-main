import { InvoiceDisplayedStatus } from '@/apiClient/v1'
import { TagVariant } from '@/design-system/Tag/Tag'

export const INVOICE_STATUS_LABELS = {
  [InvoiceDisplayedStatus.PENDING]: {
    label: 'En attente',
    variant: TagVariant.DEFAULT,
  },
  [InvoiceDisplayedStatus.PAID]: {
    label: 'Réglé',
    variant: TagVariant.SUCCESS,
  },
} as const
