import get from 'lodash.get'
import moment from 'moment'
import { requestData } from 'pass-culture-shared'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import FormField from './layout/FormField'
import SubmitButton from './layout/SubmitButton'
import { mergeForm } from '../reducers/form'
import eventSelector from '../selectors/event'
import offerSelector from '../selectors/offer'
import timezoneSelector from '../selectors/timezone'
import venueSelector from '../selectors/venue'
import occurencesSelector from '../selectors/occurences'
import { NEW } from '../utils/config'
import { getIsDisabled } from '../utils/form'

import Form from './layout/Form'
import Field from './layout/Field'
import Submit from './layout/Submit'


class OccurenceForm extends Component {

  constructor () {
    super()
    this.state = {
      apiPath: null,
      date: null,
      highlightedDates: null,
      method: null,
      time: null
    }
  }

  static getDerivedStateFromProps (nextProps) {
    const {
      event,
      form,
      occurences,
      occurence,
      offer,
      tz
    } = nextProps

    const {
      beginningDatetime,
      endDatetime,
      id
    } = (occurence || {})

    const {
      bookingLimitDatetime
    } = (offer || {})

    const eventOccurenceIdOrNew = id || NEW
    const formOccurence = get(form, `eventOccurencesById.${eventOccurenceIdOrNew}`, {})
    const isEmptyOccurenceForm = Object.keys(formOccurence).length === 0
    const isEventOccurenceFrozen = event && typeof event.lastProviderId === 'string'
    const offerId = get(offer, 'id')
    const offerIdOrNew = offerId || NEW

    let apiPath, method, storeKey
    if (isEventOccurenceFrozen || isEmptyOccurenceForm) {
      apiPath = `offers${offerId ? `/${offerId}` : ''}`
      method = offerId ? 'PATCH' : 'POST'
      storeKey = 'offers'
    } else {
      apiPath = `eventOccurences${id ? `/${id}` : ''}`
      method = id ? 'PATCH' : 'POST'
      storeKey = 'eventOccurences'
    }

    const formDate = formOccurence.date
    const date = beginningDatetime && moment.tz(beginningDatetime, tz)
    const bookingDate = formOccurence.bookingDate
      || (bookingLimitDatetime && moment.tz(bookingLimitDatetime, tz))
      || (formDate && formDate.clone().subtract(2, 'days'))
    const filterBookingDate = date || formDate
    return {
      apiPath,
      bookingDate,
      date,
      endTime: endDatetime && moment.tz(endDatetime, tz).format('HH:mm'),
      eventOccurenceIdOrNew,
      filterBookingDate,
      formDate,
      highlightedDates: occurences &&
        occurences.map(o => moment(o.beginningDatetime)),
      isEmptyOccurenceForm,
      isEventOccurenceFrozen,
      method,
      offerIdOrNew,
      storeKey,
      time: date && date.format('HH:mm'),
    }
  }

  onCancelClick = () => {
    const {
      history,
      occasion
    } = this.props
    const {
      id
    } = (occasion || {})
    history.push(`/offres/${id}/dates`)
  }

  handleSuccessData = (state, action) => {
    const {
      form,
      history,
      occasion,
      requestData,
      venue,
      tz
    } = this.props
    const {
      id
    } = (occasion || {})
    const {
      method,
      offerIdOrNew,
      storeKey
    } = this.state


    // ON A POST/PATCH EVENT OCCURENCE SUCCESS
    // WE CAN CHECK IF WE NEED TO POST/PATCH ALSO
    // AN ASSOCIATED OFFER
    const formOffer = get(form, `offersById.${offerIdOrNew}`) || {}
    if (storeKey !== 'offers' && method !== 'DELETE') {

      if (Object.keys(formOffer).length) {

        if (formOffer.bookingDate) {
          formOffer.bookingLimitDatetime = formOffer.bookingDate
            .tz(tz)
            .utc()
            .format()
        }

        const body = Object.assign({
          eventOccurenceId: action.data.id,
          offererId: venue.managingOffererId,
        }, formOffer)

        requestData(
          method,
          'offers',
          {
            body,
            key: 'offers'
          }
        )
      }
    }

    history.push(`/offres/${id}/dates`)

  }

  render () {
    const {
      event,
      occurence,
      offer,
      venue,
      tz,
    } = this.props
    const {
      id,
    } = occurence || {}
    const {
      price,
      available,
      pmrGroupSize
    } = (offer || {})
    const {
      apiPath,
      bookingDate,
      endTime,
      date,
      eventOccurenceIdOrNew,
      filterBookingDate,
      highlightedDates,
      isEmptyOccurenceForm,
      isEventOccurenceFrozen,
      method,
      offerIdOrNew,
      storeKey,
      time
    } = this.state

    return (
      <Form
        name='occurence'
        TagName='tr'
        className='occurence-form'
        action={apiPath}
        handleSuccess={this.handleSuccessData}
        data={this.state}
        readOnly={isEventOccurenceFrozen}
        layout='input-only'
        size="small"
      >
        <td>
          <Field name='date' required highlightedDates={highlightedDates} title='Date' />
        </td>
        <td>
          <Field name='time' required title='Heure' />
        </td>
        <td>
          <Field type='time' name='endTime' required title='Heure de fin' />
        </td>
        <td title='Vide si gratuit'>
          <Field name="price" required placeholder='Gratuit' title='Prix' />
        </td>
        <td title='Laissez vide si pas de limite'>
          <Field name='bookingDate' type='date' filterDate={date => filterBookingDate && date < filterBookingDate} placeholder="Laissez vide si pas de limite"/>
        </td>
        <td title='Laissez vide si pas de limite'>
          <Field name='available' type='number' title='Places disponibles' />
        </td>
        <td>
          <button
            className="button is-secondary is-small"
            onClick={this.onCancelClick}
          >Annuler</button>
        </td>
        <td>
          <Submit className="button is-primary is-small"
            // getBody={form => {

            //   // MAYBE WE CAN ONLY TOUCH ON THE OFFER
            //   if (isEventOccurenceFrozen || isEmptyOccurenceForm) {
            //     const formOffer = get(form, `offersById.${offerIdOrNew}`)

            //     if (formOffer.bookingDate) {
            //       formOffer.bookingLimitDatetime = formOffer.bookingDate
            //         .tz(tz)
            //         .utc()
            //         .format()
            //     }

            //     const body = Object.assign({
            //         eventOccurenceId: id,
            //         offererId: venue.managingOffererId
            //       }, formOffer)
            //     return body
            //   }

            //   // ELSE IT IS AN OCCURENCE FORM
            //   const eo = get(form, `eventOccurencesById.${eventOccurenceIdOrNew}`)
            //   if (!eo) {
            //     console.warn('weird eo form is empty')
            //     return
            //   }
            //   const [hour, minute] = (eo.time || time).split(':')
            //   const beginningDatetime = (eo.date || date)
            //     .tz(tz)
            //     .set({
            //       hour,
            //       minute
            //     })
            //   const [endHour, endMinute] = (eo.endTime || endTime).split(':')
            //   const endDatetime = beginningDatetime.clone()
            //                                        .set({
            //                                           hour: endHour,
            //                                           minute: endMinute
            //                                         })
            //   if (endDatetime < beginningDatetime) {
            //     endDatetime.add(1, 'days')
            //   }
            //   return Object.assign({}, eo, {
            //     beginningDatetime: beginningDatetime.utc().format(),
            //     endDatetime: endDatetime.utc().format(),
            //     eventId: get(event, 'id'),
            //     venueId: get(venue, 'id'),
            //   })
            // }}
            // getIsDisabled={form => {
            //   const isDisabledBecauseOffer = getIsDisabled(
            //     get(form, `offersById.${offerIdOrNew}`),
            //     ['available', 'bookingDate', 'price'],
            //     typeof offer === 'undefined'
            //   )

            //   if (isEventOccurenceFrozen) {
            //     return isDisabledBecauseOffer
            //   }


            //   if (isDisabledBecauseOffer) {

            //     const isDisabledBecauseEventOccurence = getIsDisabled(
            //       get(form, `eventOccurencesById.${eventOccurenceIdOrNew}`),
            //       ['date', 'endTime', 'time',],
            //       typeof occurence === 'undefined'
            //     )

            //     return isDisabledBecauseEventOccurence
            //   }

            //   return false
            // }}
          >
            Valider
          </Submit>
        </td>
        <td></td>
      </Form>
    )
  }
}

export default connect(
  (state, ownProps) => {
    const {eventId, venueId} = ownProps.occasion || {}
    const occurenceId = get(ownProps, 'occurence.id')
    return {
      form: state.form,
      event: eventSelector(state, eventId),
      offer: offerSelector(state, occurenceId),
      venue: venueSelector(state, venueId),
      tz: timezoneSelector(state, venueId),
      occurences: occurencesSelector(state, venueId, eventId),
    }
  },
  { mergeForm, requestData }
)(OccurenceForm)
