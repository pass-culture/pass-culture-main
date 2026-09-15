import type { InvoiceResponseV2Model } from '@/apiClient/v1'

export type ExtendedInvoiceResponseV2Model = InvoiceResponseV2Model & {
  id: string
  isCaledonian?: boolean
}
