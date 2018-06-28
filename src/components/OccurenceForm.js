import get from 'lodash.get'
import moment from 'moment'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import FormField from './layout/FormField'
import SubmitButton from './layout/SubmitButton'
import createEventSelector from '../selectors/createEvent'
import createTimezoneSelector from '../selectors/createTimezone'
import createVenueSelector from '../selectors/createVenue'
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
      occurences,
      occurence,
      tz
    } = nextProps
    const {
      beginningDatetime,
      endDatetime,
      id
    } = (occurence || {})
    const date = beginningDatetime && moment.tz(beginningDatetime, tz)
    return {
      apiPath: `eventOccurences${id ? `/${id}` : ''}`,
      date,
      endTime: endDatetime && moment.tz(endDatetime, tz).format('HH:mm'),
      highlightedDates: occurences &&
        occurences.map(o => moment(o.beginningDatetime)),
      method: id ? 'PATCH' : 'POST',
      time: date && date.format('HH:mm'),
    }
  }

  render () {
    const {
      event,
      occasion,
      occurence,
      onDeleteClick,
      venue,
      tz,
    } = this.props
    const {
      id,
      beginningDatetime,
      endDatetime,
      offer,
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
      date,
      highlightedDates,
      method,
      time,
      endTime
    } = this.state
    console.log("OC", occurence)
    const eventOccurenceIdOrNew = id || NEW

    return (
      <tr className='occurence-form'>
        <td>
          <FormField
            collectionName="eventOccurences"
            defaultValue={date}
            entityId={eventOccurenceIdOrNew}
            name="date"
            required
            type="date"
            className='is-small'
            highlightedDates={highlightedDates}
          />
        </td>
        <td>
          <FormField
            className='is-small'
            collectionName="eventOccurences"
            defaultValue={time}
            entityId={eventOccurenceIdOrNew}
            name="time"
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
            required
            type="time"
          />
        </td>
        <td title='Vide si gratuit'>
          <FormField
            collectionName="eventOccurences"
            entityId={eventOccurenceIdOrNew}
            defaultValue={price}
            min={0}
            name="price"
            required
            type="number"
            className='is-small'
            placeholder='Vide si gratuit'
          />
        </td>
        <td title='Laissez vide si pas de limite'>
          <FormField
            collectionName="eventOccurences"
            entityId={eventOccurenceIdOrNew}
            min={0}
            name="available"
            placeholder="Laissez vide si pas de limite"
            type="number"
            className='is-small'
            defaultValue={available}
          />
        </td>
        <td title='Laissez vide si pas de limite'>
          <FormField
            collectionName="eventOccurences"
            entityId={eventOccurenceIdOrNew}
            min={0}
            name="pmrGroupSize"
            placeholder="Laissez vide si pas de limite"
            type="number"
            className='is-small'
            defaultValue={pmrGroupSize}
          />
        </td>
        <td>
          <button
            className="button is-secondary is-small"
            onClick={e => onDeleteClick && onDeleteClick(e)}
          >Annuler</button>
        </td>
        <td>
          <SubmitButton
            className="button is-primary is-small"
            getBody={form => {
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
            getIsDisabled={form => getIsDisabled(
              get(form, `eventOccurencesById.${eventOccurenceIdOrNew}`),
              ['date', 'time', 'endTime'],
              !occurence
            )}
            handleSuccess={e => onDeleteClick && onDeleteClick()}
            method={method}
            path={apiPath}
            storeKey="eventOccurences"
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
const venueSelector = createVenueSelector()
const timezoneSelector = createTimezoneSelector(venueSelector)

export default connect(
  (state, ownProps) => ({
    event: eventSelector(state, get(ownProps, 'occasion.eventId')),
    venue: venueSelector(state, get(ownProps, 'occasion.venueId')),
    tz: timezoneSelector(state, get(ownProps, 'occasion.venueId'))
  })
)(OccurenceForm)
