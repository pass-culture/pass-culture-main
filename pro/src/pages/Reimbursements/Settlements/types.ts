import type { InvoiceResponseModel } from '@/apiClient/v1'

export type ExtendedInvoiceResponseModel = InvoiceResponseModel & {
  id: string
  isCaledonian?: boolean
}
