/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import moment from 'moment'
import PropTypes from 'prop-types'

import withForm from '../forms/withForm'
import { isSameDayInEachTimezone, getPrice } from '../../helpers'
import { CalendarField, HiddenField, SelectField } from '../forms/inputs'

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
  const userChosen = bookables.filter(o =>
    // l'offer est OK si elle est le même jour
    // que la date selectionnee par l'user dans le calendrier
    isSameDayInEachTimezone(selection.date, o.beginningDatetime)
  )
  const issingle = userChosen && userChosen.length === 1
  if (!userChosen || !issingle) return resetObj
  return {
    price: userChosen[0].price,
    // NOTE -> pas de gestion de stock
    quantity: 1,
    stockId: userChosen[0].id,
    time: userChosen[0].id,
  }
}

const onTimeUpdates = (selection, name, formValues) => {
  const resetObj = {}
  if (!selection || formValues.stockId) return resetObj
  const { bookables } = formValues
  const booked = bookables.filter(o => o.id === selection)
  return {
    price: booked[0].price,
    // NOTE -> pas de gestion de stock
    quantity: 1,
    stockId: booked[0].id,
  }
}

class BookingFormComponent extends React.PureComponent {
  getCalendarProvider = () => {
    const { formValues } = this.props
    const results = formValues.bookables.map(o => o.beginningDatetime)
    return results
  }

  parseHoursByStockId = () => {
    const { formValues } = this.props
    const { date, bookables } = formValues
    if (!date || !date.date) return []
    return bookables
      .filter(o => isSameDayInEachTimezone(date.date, o.beginningDatetime))
      .map(obj => {
        // parse les infos d'une offre
        // pour être affichée dans la selectbox
        const time = obj.beginningDatetime.format('HH:mm')
        const devised = getPrice(obj.price)
        const label = `${time} - ${devised}`
        return { id: obj.id, label }
      })
  }

  render() {
    const calendarDates = this.getCalendarProvider()
    const hoursAndPrices = this.parseHoursByStockId()
    const { formValues } = this.props
    const { stockId, price } = formValues
    return (
      <React.Fragment>
        <HiddenField name="price" />
        <HiddenField name="stockId" />
        <HiddenField name="quantity" />
        <CalendarField
          name="date"
          help="This is help"
          provider={calendarDates}
          label="Choisissez une date"
          className="text-center"
          placeholder={moment().format('DD MMMM YYYY')}
        />
        {hoursAndPrices && (
          <SelectField
            name="time"
            provider={hoursAndPrices}
            placeholder="Heure et prix"
            label="Choisissez une heure"
            className="text-center"
          />
        )}
        {stockId && (
          <p className="text-center">
            <span className="is-block">Vous êtes sur le point de réserver</span>
            <span className="is-block">cette offre pour {price}€</span>
          </p>
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
