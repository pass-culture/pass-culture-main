import { DATE_FILTER } from '../../../components/pages/search/Filters/filtersEnums'
import { AppSearchFields } from '../constants'
import { TIME } from './timeFilters'

export const buildNumericFilters = params => {
  return [
    ...buildOfferPriceRangePredicate(params),
    ...buildDatePredicate(params),
    ...buildHomepageDatePredicate(params),
    ...buildNewestOffersPredicate(params),
  ]
}

const MAX_PRICE = 30000

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
  if (date && timeRange && timeRange.length) return buildDateAndTimePredicate({ date, timeRange })
  if (date) return buildDateOnlyPredicate(date)
  if (timeRange && timeRange.length) return buildTimeOnlyPredicate(timeRange)
  return []
}

const buildHomepageDatePredicate = params => {
  const { beginningDatetime, endingDatetime } = params
  if (!beginningDatetime && !endingDatetime) return []

  const filter = {}
  if (beginningDatetime)
    filter['from'] = TIME.roundToNearestFiveMinutes(beginningDatetime).toISOString()
  if (endingDatetime) filter['to'] = TIME.roundToNearestFiveMinutes(endingDatetime).toISOString()

  return [{ [AppSearchFields.dates]: filter }]
}

const buildTimeOnlyPredicate = timeRange => {
  if (timeRange.length === 0) return []
  const [from, to] = TIME.computeTimeRangeFromHoursToSeconds(timeRange)
  return [{ [AppSearchFields.times]: { from, to } }]
}

// Attention à la timezone. Utiliser le departementCode?
const buildDateAndTimePredicate = ({ date, timeRange }) => {
  let dateFilter
  switch (date.option) {
    case DATE_FILTER.CURRENT_WEEK.value:
      dateFilter = TIME.WEEK.getAllFromTimeRangeAndDate(date.selectedDate, timeRange)
      break
    case DATE_FILTER.CURRENT_WEEK_END.value:
      dateFilter = TIME.WEEK_END.getAllFromTimeRangeAndDate(date.selectedDate, timeRange)
      break
    default:
      dateFilter = [TIME.getAllFromTimeRangeAndDate(date.selectedDate, timeRange)]
  }

  return dateFilter.map(([from, to]) => ({
    [AppSearchFields.dates]: {
      from: new Date(from).toISOString(),
      to: new Date(to).toISOString(),
    },
  }))
}

const buildDateOnlyPredicate = date => {
  let from, to
  switch (date.option) {
    case DATE_FILTER.TODAY.value:
      from = date.selectedDate
      to = TIME.getEndOfDay(date.selectedDate)
      break
    case DATE_FILTER.CURRENT_WEEK.value:
      from = date.selectedDate
      to = TIME.getEndOfWeek(date.selectedDate)
      break
    case DATE_FILTER.CURRENT_WEEK_END.value:
      from = TIME.getStartOfWeekEnd(date.selectedDate)
      to = TIME.getEndOfWeek(date.selectedDate)
      break
    case DATE_FILTER.USER_PICK.value:
      from = TIME.getStartOfDay(date.selectedDate)
      to = TIME.getEndOfDay(date.selectedDate)
      break
  }

  return [
    {
      [AppSearchFields.dates]: {
        from: new Date(from).toISOString(),
        to: new Date(to).toISOString(),
      },
    },
  ]
}

const buildNewestOffersPredicate = params => {
  const { offerIsNew } = params
  if (!offerIsNew) return []

  const now = TIME.roundToNearestFiveMinutes(new Date())
  const to = now.toISOString()

  const fifteenDaysAgo = new Date(now.setDate(now.getDate() - 15))
  const from = fifteenDaysAgo.toISOString()

  return [{ [AppSearchFields.stocks_date_created]: { from, to } }]
}
