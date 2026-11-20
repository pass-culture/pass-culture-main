import { format, startOfDay, subDays } from 'date-fns'

import type { InvoiceDisplayedStatus } from '@/apiClient/v1'
import { FORMAT_ISO_DATE_ONLY, getToday } from '@/commons/utils/date'

const DEFAULT_INVOICES_PERIOD = 30
export const DEFAULT_INVOICES_FILTERS = {
  periodBeginningDate: format(
    startOfDay(subDays(getToday(), DEFAULT_INVOICES_PERIOD)),
    FORMAT_ISO_DATE_ONLY
  ),
  periodEndingDate: format(startOfDay(getToday()), FORMAT_ISO_DATE_ONLY),
}

export const DOWNLOAD_INVOICE_LABEL = 'Télécharger le justificatif (.pdf)'

export const DOWNLOAD_REIMBURSEMENTS_LABEL =
  'Télécharger les remboursements (.csv)'

export const ALL_INVOICE_STATUS = 'ALL_INVOICE_STATUS'
export type STATUS_FILTER = InvoiceDisplayedStatus | typeof ALL_INVOICE_STATUS
