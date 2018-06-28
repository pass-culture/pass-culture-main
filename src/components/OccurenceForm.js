import get from 'lodash.get'
import moment from 'moment'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import FormField from './layout/FormField'
import SubmitButton from './layout/SubmitButton'
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

    const isEventOccurenceFrozen = typeof event.lastProviderId !== 'undefined'
    const offerId = get(offer, 'id')
    const offerIdOrNew = offerId || NEW

    let apiPath, method, storeKey
    if (isEventOccurenceFrozen) {
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
      eventOccurenceIdOrNew: id || NEW,
      highlightedDates: occurences &&
        occurences.map(o => moment(o.beginningDatetime)),
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
      method,
      onEditChange,
      requestData,
      venue
    } = this.props
    const {
      offerIdOrNew
    } = this.state

    // ON A POST EVENT OCCURENCE SUCCESS
    // WE CAN CHECK IF WE NEED TO POST ALSO
    // AN ASSOCIATED OFFER
    if (method === 'POST' ) {
      const offerForm = form.offersById[offerIdOrNew] || {}
      if (Object.keys(offerForm).length) {
        requestData(
          'POST',
          'offers',
          {
            body: Object.key({
              eventOccurenceId: action.data.id,
              offererId: venue.managingOffererId
            }, offerForm),
            key: 'offers'
          }
        )
      }
    } else {
      onEditChange && onEditChange(false)
    }
  }

  render () {
    const {
      event,
      occasion,
      occurence,
      offer,
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
    } = get(offer, '0') || {}
    const {
      durationMinutes,
    } = (occasion || {})
    const {
      apiPath,
      endTime,
      date,
      eventOccurenceIdOrNew,
      highlightedDates,
      isEventOccurenceFrozen,
      method,
      offerIdOrNew,
      storeKey,
      time
    } = this.state

    return (
      <tr className='occurence-form'>
        <td>
          {
            isEventOccurenceFrozen
              ? date.format('DD/MM/YYYY')
              : <FormField
                  className='is-small'
                  collectionName="eventOccurences"
                  defaultValue={date}
                  entityId={eventOccurenceIdOrNew}
                  highlightedDates={highlightedDates}
                  name="date"
                  readOnly={isEventOccurenceFrozen}
                  required
                  type="date"
                />
          }
        </td>
        <td>
          {
            isEventOccurenceFrozen
              ? time
              : <FormField
                  className='is-small'
                  collectionName="eventOccurences"
                  defaultValue={time}
                  entityId={eventOccurenceIdOrNew}
                  name="time"
                  required
                  type="time"
                />
          }
        </td>
        <td>
          {
            isEventOccurenceFrozen
              ? endTime
              : <FormField
                  className='is-small'
                  collectionName="eventOccurences"
                  defaultValue={endTime}
                  entityId={eventOccurenceIdOrNew}
                  name="endTime"
                  required
                  type="time"
                />
          }
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
              if (isEventOccurenceFrozen) {
                return Object.assign({
                    eventOccurenceId: id,
                    offererId: venue.managingOffererId
                  }, get(form, `offersById.${offerIdOrNew}`))
              }

              // ELSE IT IS AN OCCURENCE FORM
              const eo = get(form, `eventOccurencesById.${eventOccurenceIdOrNew}`)
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

              const isDisabledBecauseEventOccurence = getIsDisabled(
                get(form, `eventOccurencesById.${eventOccurenceIdOrNew}`),
                ['date', 'endTime', 'time',],
                typeof occurence === 'undefined'
              )
              if (isDisabledBecauseEventOccurence) {
                return false
              }

              return isDisabledBecauseOffer
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
  (state, ownProps) => ({
    form: state.form,
    event: eventSelector(state, get(ownProps, 'occasion.eventId')),
    offer: offerSelector(state, get(ownProps, 'occurence.offerId')),
    venue: venueSelector(state, get(ownProps, 'occasion.venueId')),
    tz: timezoneSelector(state, get(ownProps, 'occasion.venueId')),
    occurences: occurencesSelector(state, get(ownProps, 'occasion.venueId'), get(ownProps, 'occasion.eventId')),
  })
)(OccurenceForm)
