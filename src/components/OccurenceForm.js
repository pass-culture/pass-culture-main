import get from 'lodash.get'
import moment from 'moment'
import React, { Component } from 'react'

import FormField from './layout/FormField'
import SubmitButton from './layout/SubmitButton'
import { mergeForm } from '../reducers/form'
import selectCurrentOccurences from '../selectors/currentOccurences'
import { NEW } from '../utils/config'
import { getIsDisabled } from '../utils/form'

class OccurenceForm extends Component {

  constructor () {
    super()
    this.state = {
      highlightedDates: null
    }
  }

  static getDerivedStateFromProps (nextProps) {
    const {
      currentOccurences,
      occurence
    } = nextProps
    const {
      id
    } = (occurence || {})
    return {
      apiPath: `eventOccurences${id ? `/${id}` : ''}`,
      highlightedDates: currentOccurences &&
        currentOccurences.map(o => moment(o.beginningDatetime)),
      method: id ? 'PATCH' : 'POST'
    }
  }

  render () {
    const {
      currentOccasion,
      currentOccurences,
      occurence,
      onDeleteClick,
    } = this.props
    const {
      id,
      available,
      eventOccurence,
      selectedVenueId,
      price,
      beginningDatetime,
      groupSize,
      pmrGroupSize
    } = occurence || {}
    const {
      durationMinutes,
    } = (currentOccasion || {})
    const {
      apiPath,
      highlightedDates,
      method
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
              const [hour, minute] = eo.time.split(':')
              const beginningDatetime = eo.date.set({
                hour,
                minute,
              })
              const endDatetime = beginningDatetime.clone().add(durationMinutes, 'minutes')
              return {
                beginningDatetime: beginningDatetime.format(), // ignores the GMT part of the date
                endDatetime: endDatetime.format(),
                groupSize: eo.groupSize,
                pmrGroupSize: eo.pmrGroupSize,
                price: eo.price,
                eventId: get(currentOccasion, 'event.id'),
                venueId: currentOccasion.venueId,
              }
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

export default OccurenceForm
