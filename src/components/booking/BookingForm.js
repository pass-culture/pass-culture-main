import React from 'react'
import moment from 'moment'
import get from 'lodash.get'
import PropTypes from 'prop-types'

import withForm from '../forms/withForm'
import { TimeField, CalendarField } from '../forms/fields'

const parseAvailableDates = item => {
  const format = 'YYYYMMDD'
  const stocks = get(item, 'offer.stocks')
  if (!stocks) return []
  const filtered = stocks
    .filter(o => o.available)
    .map(o => moment(o.bookingLimitDatetime).format(format))
  return filtered
}

class BookingFormComponent extends React.PureComponent {
  render() {
    const { item } = this.props
    console.log('BookingFormComponent --->', item)
    const availables = parseAvailableDates(item)
    return (
      <React.Fragment>
        <CalendarField
          name="date"
          availables={availables}
          label="Choisissez une date"
        />
        <TimeField name="time" label="Choisissez une heure" />
      </React.Fragment>
    )
  }
}

BookingFormComponent.defaultProps = {
  item: null,
}

BookingFormComponent.propTypes = {
  item: PropTypes.object,
}

const BookingForm = withForm(BookingFormComponent, null, null)
export default BookingForm
