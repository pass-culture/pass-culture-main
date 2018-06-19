import get from 'lodash.get'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import FormField from './layout/FormField'
import Label from './layout/Label'
import SubmitButton from './layout/SubmitButton'
import { mergeForm } from '../reducers/form'
import selectEventOccurenceForm from '../selectors/eventOccurenceForm'
import { NEW } from '../utils/config'

const OccurenceForm = ({
  currentOccasion,
  eventOccurence,
  eventOccurenceForm,
  onDeleteClick,
  isNew,
  selectedVenueId,
  time
}) => {
  const {
    durationMinutes,
    id
  } = (currentOccasion || {})
  const {
    offer
  } = (eventOccurence || {})
  const {
    beginningDatetime,
    eventOccurenceIdOrNew
  } = (eventOccurenceForm || {})
  return (
    <tr className='occurence-form'>
      <td>
        <FormField
          collectionName="eventOccurences"
          entityId={eventOccurenceIdOrNew}
          name="date"
          required
          type="date"
          className='is-small'
        />
      </td>
      <td>
        <FormField
          collectionName="eventOccurences"
          entityId={eventOccurenceIdOrNew}
          name="time"
          required
          type="time"
          className='is-small'
        />
      </td>
      <td>
        <FormField
          collectionName="eventOccurences"
          entityId={get(offer, 'id')}
          defaultValue={0}
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
          entityId={get(offer, 'groupSize')}
          min={0}
          name="groupSize"
          placeholder="Laissez vide si pas de limite"
          type="number"
          className='is-small'
        />
      </td>
      <td>
        <FormField
          collectionName="eventOccurences"
          entityId={get(offer, 'pmrGroupSize')}
          min={0}
          name="pmrGroupSize"
          placeholder="Laissez vide si pas de limite"
          type="number"
          className='is-small'
        />
      </td>
      <td>
        <SubmitButton
          className="button is-primary is-small"
          getBody={form => {
            const eo = get(form, `eventOccurencesById.${eventOccurenceIdOrNew}`)
            const endDatetime = beginningDatetime.add(durationMinutes, 'minutes')
            return Object.assign({
              beginningDatetime,
              endDatetime,
              eventId: id,
              venueId: selectedVenueId
            }, eo)
          }}
          getIsDisabled={form => !beginningDatetime}
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

export default connect(
  (state, ownProps) => ({
    eventOccurenceForm: selectEventOccurenceForm(state, ownProps)
  }),
  { mergeForm }
)(OccurenceForm)
