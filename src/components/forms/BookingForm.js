import React from 'react'
import moment from 'moment'
// import get from 'lodash.get'
import PropTypes from 'prop-types'

import withForm from './withForm'
import { CalendarField, HiddenField, SelectField } from './inputs'

const getCalendarProvider = parsed => parsed.map(obj => obj.beginningDatetime)

/**
 * Calcule les valeurs du form
 * En fonction de la date selectionnée par l'user
 *
 * NOTE -> Howto implement calculator: https://codesandbox.io/s/oq52p6v96y
 * FIXME -> hot-reload cause console.error
 */
const onCalendarUpdates = (selection, name, allvalues) => {
  if (!selection || !selection.date) return {}
  // iteration sur l'array bookables
  // recupere tous les events pour la selection par l'user
  const { bookables } = allvalues
  const momentvalue = selection.date
  const selected = bookables.filter(o =>
    // l'offer est OK si elle est le même jour
    // que la date selectionnee par l'user dans le calendrier
    momentvalue.isSame(o.beginningDatetime, 'day')
  )
  const issingle = selected && selected.length === 1
  if (!selected || !issingle) return {}
  return {
    price: selected[0].price,
    // NOTE -> pas de gestion de stock
    quantity: 1,
    stockId: selected[0].stockId,
  }
}

class BookingFormComponent extends React.PureComponent {
  parseHoursByStockId = dates => {
    const { formValues } = this.props
    if (!formValues.stockId) return []
    const obj = dates[formValues.stockId] || null
    if (!obj) return []
    return []
  }

  render() {
    const { formValues } = this.props
    const { bookables } = formValues
    const dates = getCalendarProvider(bookables)
    const availableHours = this.parseHoursByStockId(bookables)
    return (
      <React.Fragment>
        <HiddenField name="price" />
        <HiddenField name="stockId" />
        <HiddenField name="quantity" />
        <CalendarField
          name="date"
          help="This is help"
          provider={dates}
          label="Choisissez une date"
          placeholder={moment().format('DD MMMM YYYY')}
        />
        {availableHours && (
          <SelectField
            name="time"
            placeholder="Horaire"
            provider={availableHours}
            label="Choisissez une heure"
          />
        )}
      </React.Fragment>
    )
  }
}

BookingFormComponent.defaultProps = {
  formValues: null,
}

BookingFormComponent.propTypes = {
  formValues: PropTypes.object,
}

/* -------- form validators --------  */
const validator = null

/* -------- form calculators --------  */
const calculator = [
  {
    field: 'date',
    updates: onCalendarUpdates,
  },
]

const BookingForm = withForm(BookingFormComponent, validator, calculator)
export default BookingForm
