import { DATE_FILTER } from '../../../components/pages/search/Filters/filtersEnums'
import {
  computeTimeRangeFromHoursToSeconds,
  TIMESTAMP,
} from '../../../components/pages/search/utils/date/time'
import { AppSearchFields } from '../constants'

export const buildNumericFilters = params => {
  return [
    ...buildOfferPriceRangePredicate(params),
    ...buildDatePredicate(params),
    ...buildHomepageDatePredicate(params),
    ...buildNewestOffersPredicate(params),
  ]
}

const MAX_PRICE = 30000

// Filter okey on search a long as we store prices as cents
const buildOfferPriceRangePredicate = params => {
  const { offerIsFree, priceRange } = params
  if (offerIsFree) return [{ [AppSearchFields.prices]: { to: 1 } }] // to is exclusive
  if (!priceRange) return [{ [AppSearchFields.prices]: { to: MAX_PRICE } }]

  const from = 100 * priceRange[0] || 0
  const to = Math.min(100 * priceRange[1], MAX_PRICE)

  return [{ [AppSearchFields.prices]: { from, to } }]
}

const buildDatePredicate = params => {
  const { date, timeRange } = params
  if (date && timeRange) return buildDateAndTimePredicate({ date, timeRange })
  if (date) return buildDateOnlyPredicate(date)
  if (timeRange) return buildTimeOnlyPredicate(timeRange)
  return []
}

const buildHomepageDatePredicate = params => {
  const { beginningDatetime, endingDatetime } = params
  if (!beginningDatetime && !endingDatetime) return []

  const filter = {}
  if (beginningDatetime) filter['from'] = TIMESTAMP.getFromDate(beginningDatetime)
  if (endingDatetime) filter['to'] = TIMESTAMP.getFromDate(endingDatetime)

  return [{ [AppSearchFields.dates]: filter }]
}

const buildTimeOnlyPredicate = timeRange => {
  const [from, to] = computeTimeRangeFromHoursToSeconds(timeRange)
  return [{ [AppSearchFields.times]: { from, to } }]
}

// Attention à la timezone. Utiliser le departementCode?
const buildDateAndTimePredicate = ({ date, timeRange }) => {
  let dateFilter
  switch (date.option) {
    case DATE_FILTER.CURRENT_WEEK.value:
      dateFilter = TIMESTAMP.WEEK.getAllFromTimeRangeAndDate(date.selectedDate, timeRange)
      break
    case DATE_FILTER.CURRENT_WEEK_END.value:
      dateFilter = TIMESTAMP.WEEK_END.getAllFromTimeRangeAndDate(date.selectedDate, timeRange)
      break
    default:
      dateFilter = [TIMESTAMP.getAllFromTimeRangeAndDate(date.selectedDate, timeRange)]
  }

  return dateFilter.map(([from, to]) => ({ [AppSearchFields.dates]: { from, to } }))
}

const buildDateOnlyPredicate = date => {
  let from, to
  switch (date.option) {
    case DATE_FILTER.TODAY.value:
      from = TIMESTAMP.getFromDate(date.selectedDate)
      to = TIMESTAMP.getLastOfDate(date.selectedDate)
      break
    case DATE_FILTER.CURRENT_WEEK.value:
      from = TIMESTAMP.getFromDate(date.selectedDate)
      to = TIMESTAMP.WEEK.getLastFromDate(date.selectedDate)
      break
    case DATE_FILTER.CURRENT_WEEK_END.value:
      from = TIMESTAMP.WEEK_END.getFirstFromDate(date.selectedDate)
      to = TIMESTAMP.WEEK.getLastFromDate(date.selectedDate)
      break
    case DATE_FILTER.USER_PICK.value:
      from = TIMESTAMP.getFirstOfDate(date.selectedDate)
      to = TIMESTAMP.getLastOfDate(date.selectedDate)
      break
  }

  return [{ [AppSearchFields.dates]: { from, to } }]
}

const buildNewestOffersPredicate = params => {
  const { offerIsNew } = params
  if (!offerIsNew) return []

  const now = new Date()
  const fifteenDaysAgo = new Date().setDate(now.getDate() - 15)
  const from = TIMESTAMP.getFromDate(new Date(fifteenDaysAgo))
  const to = TIMESTAMP.getFromDate(now)

  return [{ [AppSearchFields.stocks_date_created]: { from, to } }]
}
