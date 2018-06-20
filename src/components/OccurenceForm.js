import get from 'lodash.get'
import moment from 'moment'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import FormField from './layout/FormField'
import Label from './layout/Label'
import SubmitButton from './layout/SubmitButton'
import { mergeForm } from '../reducers/form'
import selectEventOccurenceForm from '../selectors/eventOccurenceForm'
import { NEW } from '../utils/config'

class OccurenceForm extends Component {

  render () {
    const {
      isNew,
      occasion,
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
    } = occasion
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
            highlightedDates={occasion.occurences.map(o => moment(o.beginningDatetime))}
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
                beginningDatetime,
                endDatetime,
                groupSize: eo.groupSize,
                pmrGroupSize: eo.pmrGroupSize,
                price: eo.price,
                eventId: occasion.id,
                venueId: occasion.venueId,
              }
            }}
            getIsDisabled={form => {
              const missingFields = ['date', 'time'].filter(f => !get(form, `eventOccurencesById.${eventOccurenceIdOrNew}.${f}`))
              return missingFields.length > 0
            }}
            handleSuccess={e => onDeleteClick && onDeleteClick()}
            method={isNew ? 'POST' : 'PATCH'}
            path={isNew ? 'eventOccurences' : `eventOccurences/${id}`}
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
