import { startOfDay, subDays, format } from 'date-fns'

import { FORMAT_ISO_DATE_ONLY, getToday } from '../../utils/date'

const DEFAULT_INVOICES_PERIOD = 30
export const DEFAULT_INVOICES_FILTERS = {
  reimbursementPointId: 'all',
  periodBeginningDate: format(
    startOfDay(subDays(getToday(), DEFAULT_INVOICES_PERIOD)),
    FORMAT_ISO_DATE_ONLY
  ),
  periodEndingDate: format(startOfDay(getToday()), FORMAT_ISO_DATE_ONLY),
}
