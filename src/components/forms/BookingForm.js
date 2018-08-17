import React from 'react'
import moment from 'moment'
import get from 'lodash.get'
import PropTypes from 'prop-types'

import withForm from './withForm'
import { CalendarField, HiddenField, SelectField } from './inputs'

/*
  const mediatedOccurences = get(
    this.props,
    'currentRecommendation.mediatedOccurences',
    []
  )
  const { tz } = this.props
  const NOW = moment()
  const { date } = this.state
  const availableDates = mediatedOccurences
    .filter(o => moment(o.offer[0].bookingLimitDatetime).isAfter(NOW))
    .map(o => moment(o.beginningDatetime).tz(tz))
  const availableMediatedOccurences = []
  const availableHours = availableDates.filter((d, index) => {
    const isFiltered = d.isSame(selectedDate || date, 'day')
    if (isFiltered) {
      availableMediatedOccurences.push(mediatedOccurences[index])
    }
    return isFiltered
  })
  return {
    availableDates,
    availableHours,
    availableMediatedOccurences,
  }
  */
const parseAvailableDates = item => {
  const { tz /* , validUntilDate */ } = item
  const stocks = get(item, 'offer.stocks')
  if (!stocks) return []
  const ifStockAvailable = o => o.available && o.available > 0
  const pickDateLimitProp = o => o.bookingLimitDatetime
  const transformDateToTimezone = d => moment(d).tz(tz)
  // const now = moment()
  // const isDateAfterNow = d => d.isAfter(now)
  // const format = 'YYYYMMDD'
  // const transformDateToFormat = o => o.format(format)
  const filtered = stocks
    .filter(ifStockAvailable)
    .map(pickDateLimitProp)
    .map(transformDateToTimezone)
  // .filter(isDateAfterNow)
  // .map(transformDateToFormat)
  return filtered
}

const parseAvailableHours = dates => {
  console.log('dates', dates)
  return []
}

class BookingFormComponent extends React.PureComponent {
  render() {
    const { item, values } = this.props
    const availableDates = parseAvailableDates(item)
    const availableHours = parseAvailableHours(availableDates)
    return (
      <React.Fragment>
        <HiddenField name="quantity" />
        <CalendarField
          name="date"
          help="This is help"
          provider={availableDates}
          label="Choisissez une date"
          placeholder={moment().format('DD MMMM YYYY')}
        />
        {availableHours && (
          <SelectField
            name="time"
            placeholder="Horaire"
            label="Choisissez une heure"
            provider={values.hours || []}
          />
        )}
      </React.Fragment>
    )
  }
}

BookingFormComponent.defaultProps = {
  item: null,
  values: null,
}

BookingFormComponent.propTypes = {
  item: PropTypes.object,
  values: PropTypes.object,
}

const BookingForm = withForm(BookingFormComponent, null, null)
export default BookingForm
