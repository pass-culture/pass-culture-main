import get from 'lodash.get'
import moment from 'moment'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import FormField from './layout/FormField'
import SubmitButton from './layout/SubmitButton'
import { requestData } from '../reducers/data'
import { mergeForm } from '../reducers/form'
import createEventSelector from '../selectors/createEvent'
import createOfferSelector from '../selectors/createOffer'
import createTimezoneSelector from '../selectors/createTimezone'
import createVenueSelector from '../selectors/createVenue'
import createOccurencesSelector from '../selectors/createOccurences'
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

    const eventOccurenceIdOrNew = id || NEW
    const formOccurence = get(form, `eventOccurencesById.${eventOccurenceIdOrNew}`, {})
    const isEmptyOccurenceForm = Object.keys(formOccurence).length === 0
    const isEventOccurenceFrozen = event && typeof event.lastProviderId === 'string'
    const offerId = get(offer, 'id')
    const offerIdOrNew = offerId || NEW
    const formOffer = get(form, `offersById.${offerIdOrNew}`)

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

    const date = beginningDatetime && moment.tz(beginningDatetime, tz)
    return {
      apiPath,
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
      mergeForm,
      occasion,
      onEditChange,
      requestData,
      venue
    } = this.props
    const {
      id
    } = (occasion || {})
    const {
      eventOccurenceIdOrNew,
      method,
      offerIdOrNew
    } = this.state


    // ON A POST/PATCH EVENT OCCURENCE SUCCESS
    // WE CAN CHECK IF WE NEED TO POST/PATCH ALSO
    // AN ASSOCIATED OFFER
    const offerForm = get(form, `offersById.${offerIdOrNew}`) || {}
    if (method !== 'DELETE') {

      // prepare the next add form to the next day
      if (method === 'POST') {
        const date = get(form, `eventOccurencesById.${eventOccurenceIdOrNew}.date`)
        // date && mergeForm('eventOccurences', NEW, 'date', date.add(1, 'days'))
      }

      if (Object.keys(offerForm).length) {

        const body = Object.assign({
          eventOccurenceId: action.data.id,
          offererId: venue.managingOffererId,
        }, offerForm)

        // price is actually compulsory for posting an offer
        // but we can let automatically set to gratuit
        if (method === 'POST' && typeof body.price === 'undefined') {
          body.price = 0
        }

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

    if (method !== 'POST') {
      history.push(`/offres/${id}/dates`)
    }
  }

  render () {
    const {
      event,
      occasion,
      occurence,
      offer,
      offerer,
      onDeleteClick,
      venue,
    } = this.props
    const {
      id,
      beginningDatetime,
      endDatetime,
    } = occurence || {}
    const {
      price,
      available,
      pmrGroupSize
    } = (offer || {})
    const {
      durationMinutes,
    } = (occasion || {})
    const {
      apiPath,
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
        </td>
        <td title='Laissez vide si pas de limite'>
          <FormField
            className='is-small'
            collectionName="offers"
            defaultValue={available}
            entityId={offerIdOrNew}
            min={0}
            name="available"
            placeholder="Laissez vide si pas de limite"
            type="number"
            className='is-small'
          />
        </td>
        <td>
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
                if (method === 'POST') {
                  // price is actually compulsory for posting an offer
                  // but we can let automatically set to gratuit
                  if (typeof body.price === 'undefined') {
                    body.price = 0
                  }
                }
                return body
              }

              // ELSE IT IS AN OCCURENCE FORM
              const eo = get(form, `eventOccurencesById.${eventOccurenceIdOrNew}`)
              if (!eo) {
                console.warn('weird eo form is empty')
                return
              }
              const [hour, minute] = (eo.time || time).split(':')
              const beginningDatetime = (eo.date || date).set({
                'hour': hour,
                'minute': minute
              })
              const [endHour, endMinute] = (eo.endTime || endTime).split(':')
              const endDatetime = beginningDatetime.clone()
                                                   .set({
                                                          hour: endHour,
                                                          minute: endMinute
                                                        })
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
                ['price'],
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

const eventSelector = createEventSelector()
const offerSelector = createOfferSelector()
const venueSelector = createVenueSelector()
const occurencesSelector = createOccurencesSelector()
const timezoneSelector = createTimezoneSelector(venueSelector)

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
