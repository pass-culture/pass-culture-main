import get from 'lodash.get'
import moment from 'moment'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import FormField from './layout/FormField'
import SubmitButton from './layout/SubmitButton'
import { requestData } from '../reducers/data'
import { mergeForm } from '../reducers/form'
import eventSelector from '../selectors/event'
import offerSelector from '../selectors/offer'
import timezoneSelector from '../selectors/timezone'
import createVenueSelector from '../selectors/createVenue'
import occurencesSelector from '../selectors/occurences'
import { NEW } from '../utils/config'
import { getIsDisabled } from '../utils/form'

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
    const bookingDate = (bookingLimitDatetime && moment.tz(bookingLimitDatetime, tz))
      || (formDate && formDate.clone().subtract(2, 'days'))
    // console.log('HEIN', formDate, formDate.subtract(2, 'days'))
    return {
      apiPath,
      bookingDate,
      date,
      endTime: endDatetime && moment.tz(endDatetime, tz).format('HH:mm'),
      eventOccurenceIdOrNew,
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
      venue
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
    const offerForm = get(form, `offersById.${offerIdOrNew}`) || {}
    if (storeKey !== 'offers' && method !== 'DELETE') {

      if (Object.keys(offerForm).length) {

        const body = Object.assign({
          eventOccurenceId: action.data.id,
          offererId: venue.managingOffererId,
        }, offerForm)

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
      highlightedDates,
      isEmptyOccurenceForm,
      isEventOccurenceFrozen,
      method,
      offerIdOrNew,
      storeKey,
      time
    } = this.state

    return (
      <tr className='occurence-form'>
        <td>
          <FormField
            className='is-small'
            collectionName="eventOccurences"
            controlClassName='has-text-centered'
            defaultValue={date}
            entityId={eventOccurenceIdOrNew}
            format='DD/MM/YYYY'
            highlightedDates={highlightedDates}
            name="date"
            readOnly={isEventOccurenceFrozen}
            required
            type="date"
          />
        </td>
        <td>
          <FormField
            className='is-small'
            collectionName="eventOccurences"
            defaultValue={time}
            entityId={eventOccurenceIdOrNew}
            name="time"
            readOnly={isEventOccurenceFrozen}
            required
            type="time"
          />
        </td>
        <td>
          <FormField
            className='is-small'
            collectionName="eventOccurences"
            defaultValue={endTime}
            entityId={eventOccurenceIdOrNew}
            name="endTime"
            readOnly={isEventOccurenceFrozen}
            required
            type="time"
          />
        </td>
        <td title='Vide si gratuit'>
          {
            false &&
              <FormField
                className='is-small'
                collectionName="offers"
                defaultValue={price}
                entityId={offerIdOrNew}
                min={0}
                name="price"
                placeholder='Vide si gratuit'
                required
                type="number"
              />
          }
          <FormField
            className='is-small'
            collectionName="offers"
            defaultValue={0}
            entityId={offerIdOrNew}
            min={0}
            name="price"
            placeholder='Gratuit'
            readOnly
            required
            type="number"
          />
        </td>
        <td title='Laissez vide si pas de limite'>
          <FormField
            className='is-small'
            collectionName="offers"
            controlClassName='has-text-centered'
            defaultValue={bookingDate}
            entityId={offerIdOrNew}
            format='DD/MM/YYYY'
            min={0}
            name="bookingDate"
            placeholder="Laissez vide si pas de limite"
            type="date"
          />
        </td>
        <td title='Laissez vide si pas de limite'>
          <FormField
            className='is-small'
            collectionName="offers"
            defaultValue={available || 0}
            entityId={offerIdOrNew}
            min={0}
            name="available"
            type="number"
          />
        </td>
        {
          false && <td>
            <FormField
              className='is-small'
              collectionName="offers"
              defaultValue={pmrGroupSize}
              entityId={offerIdOrNew}
              min={0}
              name="pmrGroupSize"
              placeholder="Laissez vide si pas de limite"
              type="number"
            />
          </td>
        }
        <td>
          <button
            className="button is-secondary is-small"
            onClick={this.onCancelClick}
          >Annuler</button>
        </td>
        <td>
          <SubmitButton
            className="button is-primary is-small"
            getBody={form => {

              // MAYBE WE CAN ONLY TOUCH ON THE OFFER
              if (isEventOccurenceFrozen || isEmptyOccurenceForm) {
                const body = Object.assign({
                    eventOccurenceId: id,
                    offererId: venue.managingOffererId
                  }, get(form, `offersById.${offerIdOrNew}`))
                return body
              }

              // ELSE IT IS AN OCCURENCE FORM
              const eo = get(form, `eventOccurencesById.${eventOccurenceIdOrNew}`)
              if (!eo) {
                console.warn('weird eo form is empty')
                return
              }
              const [hour, minute] = (eo.time || time).split(':')
              const beginningDatetime = (eo.date || date)
                .tz(tz)
                .set({
                  hour,
                  minute
                })
              //.tz(tz)
              const [endHour, endMinute] = (eo.endTime || endTime).split(':')
              const endDatetime = beginningDatetime.clone()
                                                   .set({
                                                      hour: endHour,
                                                      minute: endMinute
                                                    })
                                                    //.tz(tz)
              if (endDatetime < beginningDatetime) {
                endDatetime.add(1, 'days')
              }
              return Object.assign({}, eo, {
                beginningDatetime: beginningDatetime.utc().format(),
                endDatetime: endDatetime.utc().format(),
                eventId: get(event, 'id'),
                venueId: get(venue, 'id'),
              })
            }}
            getIsDisabled={form => {
              const isDisabledBecauseOffer = getIsDisabled(
                get(form, `offersById.${offerIdOrNew}`),
                ['available', 'bookingLimitDatetime', 'price'],
                typeof offer === 'undefined'
              )

              if (isEventOccurenceFrozen) {
                return isDisabledBecauseOffer
              }


              if (isDisabledBecauseOffer) {

                const isDisabledBecauseEventOccurence = getIsDisabled(
                  get(form, `eventOccurencesById.${eventOccurenceIdOrNew}`),
                  ['date', 'endTime', 'time',],
                  typeof occurence === 'undefined'
                )

                return isDisabledBecauseEventOccurence
              }

              return false
            }}
            handleSuccess={this.handleSuccessData}
            method={method}
            path={apiPath}
            storeKey={storeKey}
            text="Valider"
          >
            Enregistrer
          </SubmitButton>
        </td>
        <td></td>
      </tr>
    )
  }
}

const venueSelector = createVenueSelector()

export default connect(
  (state, ownProps) => {
    const eventId = get(ownProps, 'occasion.eventId')
    const occurenceId = get(ownProps, 'occurence.id')
    const venueId = get(ownProps, 'occasion.venueId')
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
