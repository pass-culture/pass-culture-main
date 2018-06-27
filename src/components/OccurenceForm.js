import get from 'lodash.get'
import moment from 'moment'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import FormField from './layout/FormField'
import SubmitButton from './layout/SubmitButton'
import createEventSelector from '../selectors/createEvent'
import createVenueSelector from '../selectors/createVenue'
import createVenuesSelector from '../selectors/createVenues'
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
      occurence
    } = nextProps
    const {
      beginningDatetime,
      id
    } = (occurence || {})
    return {
      apiPath: `eventOccurences${id ? `/${id}` : ''}`,
      date: beginningDatetime && moment(beginningDatetime),
      highlightedDates: occurences &&
        occurences.map(o => moment(o.beginningDatetime)),
      method: id ? 'PATCH' : 'POST',
      time: beginningDatetime && moment(beginningDatetime).format('HH:mm')
    }
  }

  render () {
    const {
      event,
      occasion,
      occurence,
      onDeleteClick,
      venue,
    } = this.props
    const {
      id,
      price,
      beginningDatetime,
      groupSize,
      pmrGroupSize
    } = occurence || {}
    const {
      durationMinutes,
    } = (occasion || {})
    const {
      apiPath,
      date,
      highlightedDates,
      method,
      time
    } = this.state
    const eventOccurenceIdOrNew = id || NEW

    return (
      <tr className='occurence-form'>
        <td>
          <FormField
            collectionName="eventOccurences"
            defaultValue={beginningDatetime && moment(beginningDatetime)}
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
            defaultValue={beginningDatetime && moment(beginningDatetime).format('HH:mm')}
            entityId={eventOccurenceIdOrNew}
            name="time"
            required
            type="time"
          />
        </td>
        <td>
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
        <td>
          <FormField
            collectionName="eventOccurences"
            entityId={eventOccurenceIdOrNew}
            min={0}
            name="groupSize"
            placeholder="Laissez vide si pas de limite"
            type="number"
            className='is-small'
            defaultValue={groupSize}
          />
        </td>
        <td>
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
          <SubmitButton
            className="button is-primary is-small"
            getBody={form => {
              const eo = get(form, `eventOccurencesById.${eventOccurenceIdOrNew}`)
              const [hour, minute] = (time || eo.time).split(':')
              const beginningDatetime = (date || eo.date).set({
                hour,
                minute,
              })
              const endDatetime = beginningDatetime.clone()
                .add(durationMinutes, 'minutes')
              return Object.assign({
                beginningDatetime: beginningDatetime.format(), // ignores the GMT part of the date
                endDatetime: endDatetime.format(),
                eventId: get(event, 'id'),
                venueId: get(venue, 'id'),
              }, eo)
            }}
            getIsDisabled={form => getIsDisabled(
              get(form, `eventOccurencesById.${eventOccurenceIdOrNew}`),
              ['date', 'time'],
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
        <td>
          <button
            className="delete is-small"
            onClick={e => onDeleteClick && onDeleteClick(e)}
          />
        </td>
      </tr>
    )
  }
}

const eventSelector = createEventSelector()
const venuesSelector = createVenuesSelector()
const venueSelector = createVenueSelector()

export default connect(
  (state, ownProps) => ({
    event: eventSelector(state, ownProps.occasion.eventId),
    venue: venueSelector(state, ownProps.occasion.venueId)
  })
)(OccurenceForm)
