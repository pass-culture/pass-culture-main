import React from 'react'
import moment from 'moment'
import PropTypes from 'prop-types'

import withForm from './forms/withForm'
import { getPrice } from '../helpers'
import { CalendarField, HiddenField, SelectField } from './forms/inputs'

/**
 * Calcule les valeurs du form
 * En fonction de la date selectionnée par l'user
 *
 * NOTE -> Howto implement calculator: https://codesandbox.io/s/oq52p6v96y
 * FIXME -> hot-reload cause console.error
 */
const onCalendarUpdates = (selection, name, allvalues) => {
  const resetObj = { price: null, stockId: null, time: null }
  if (!selection || !selection.date) return resetObj
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
  if (!selected || !issingle) return resetObj
  return {
    price: selected[0].price,
    // NOTE -> pas de gestion de stock
    quantity: 1,
    stockId: selected[0].stockId,
    time: selected[0].stockId,
  }
}

const onTimeUpdates = (selection, name, allvalues) => {
  const resetObj = {}
  const currentStockId = allvalues.stockId
  if (!selection || currentStockId) return resetObj
  const { bookables } = allvalues
  const selected = bookables.filter(o => o.stockId === selection)
  return {
    // price: selected[0].price,
    price: 1234567890.12345678901234567890123456789,
    // NOTE -> pas de gestion de stock
    quantity: 1,
    stockId: selected[0].stockId,
  }
}

class BookingFormComponent extends React.PureComponent {
  getCalendarProvider = () => {
    const { formValues } = this.props
    const results = formValues.bookables.map(o => o.beginningDatetime)
    return results
  }

  parseHoursByStockId = () => {
    const {
      formValues: { date, bookables },
    } = this.props
    if (!date || !date.date) return []
    return bookables
      .filter(o => {
        // verifie que la date correspond au jour
        // choisi par l'utilisateur
        const issameday = date.date.isSame(o.beginningDatetime, 'day')
        return issameday
      })
      .map(obj => {
        // parse les infos d'une offre
        // pour être affichée dans la selectbox
        const id = obj.stockId
        const time = moment(obj.beginningDatetime).format('HH:mm')
        const devised = getPrice(obj.price)
        const label = `${time} - ${devised}`
        return { id, label }
      })
  }

  render() {
    const calendarDates = this.getCalendarProvider()
    const hoursAndPrices = this.parseHoursByStockId()
    return (
      <React.Fragment>
        <HiddenField name="price" />
        <HiddenField name="stockId" />
        <HiddenField name="quantity" />
        <CalendarField
          name="date"
          provider={calendarDates}
          help="This is help"
          label="Choisissez une date"
          className="has-text-centered"
          placeholder={moment().format('DD MMMM YYYY')}
        />
        {hoursAndPrices && (
          <SelectField
            name="time"
            provider={hoursAndPrices}
            placeholder="Heure et prix"
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
  {
    field: 'time',
    updates: onTimeUpdates,
  },
]

const BookingForm = withForm(BookingFormComponent, validator, calculator)
export default BookingForm
