import { startOfDay, subDays } from 'date-fns'

import { getToday } from '../../utils/date'

export const DEFAULT_INVOICES_PERIOD = 30
export const DEFAULT_INVOICES_FILTERS = {
  reimbursementPointId: 'all',
  periodBeginningDate: startOfDay(subDays(getToday(), DEFAULT_INVOICES_PERIOD)),
  periodEndingDate: startOfDay(getToday()),
}
