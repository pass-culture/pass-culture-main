import { InvoiceStatus } from '@/apiClient/v1'
import { TagVariant } from '@/design-system/Tag/Tag'

export const INVOICE_STATUS_LABELS = {
  [InvoiceStatus.PENDING]: {
    label: 'En attente',
    variant: TagVariant.DEFAULT,
  },
  [InvoiceStatus.PENDING_PAYMENT]: {
    label: 'En attente',
    variant: TagVariant.DEFAULT,
  },
  [InvoiceStatus.PAID]: {
    label: 'Réglé',
    variant: TagVariant.SUCCESS,
  },
} as const
