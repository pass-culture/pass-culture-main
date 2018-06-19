import get from 'lodash.get'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import FormField from './layout/FormField'
import Label from './layout/Label'
import SubmitButton from './layout/SubmitButton'
import { mergeForm } from '../reducers/form'
import selectEventOccurenceForm from '../selectors/eventOccurenceForm'
import { NEW } from '../utils/config'

const OccurenceForm = ({
  eventOccurence,
  eventOccurenceForm,
  match: { params: { occasionId } },
  id,
  isNew,
  selectedVenueId,
  time
}) => {
  const {
    offer
  } = (eventOccurence || {})
  const {
    beginningDatetime,
    eventOccurenceIdOrNew
  } = (eventOccurenceForm || {})

  console.log("selectedVenueId", selectedVenueId)

  return (
    <tr>
      <td>
        <FormField
          collectionName="eventOccurences"
          entityId={eventOccurenceIdOrNew}
          label={<Label title="Date :" />}
          name="date"
          required
          type="date"
        />
      </td>
      <td>
        <FormField
          collectionName="eventOccurences"
          entityId={eventOccurenceIdOrNew}
          label={<Label title="Heure :" />}
          name="time"
          required
          type="time"
        />
      </td>
      <td>
        <FormField
          collectionName="eventOccurences"
          entityId={get(offer, 'id')}
          defaultValue={0}
          label={<Label title="Prix (€) :" />}
          min={0}
          name="price"
          required
          type="number"
        />
      </td>
      <td>
        <FormField
          collectionName="eventOccurences"
          entityId={get(offer, 'groupSize')}
          label={<Label title="Nombre de places" />}
          min={0}
          name="groupSize"
          placeholder="Laissez vide si pas de limite"
          type="number"
        />
      </td>
      <td>
        <FormField
          collectionName="eventOccurences"
          entityId={get(offer, 'pmrGroupSize')}
          label={<Label title="Places en PMR" />}
          min={0}
          name="pmrGroupSize"
          placeholder="Laissez vide si pas de limite"
          type="number"
        />
      </td>
      <td>
        <SubmitButton
          className="button is-primary is-medium"
          getBody={form => {
            const eo = get(form, `eventOccurencesById.${eventOccurenceIdOrNew}`)
            console.log('eo', eo)
            return Object.assign({
              beginningDatetime,
              eventId: occasionId,
              venueId: selectedVenueId
            }, eo)
          }}
          getIsDisabled={form => !beginningDatetime}
          method={isNew ? 'POST' : 'PATCH'}
          path={isNew ? 'eventOccurences' : `eventOccurences/${id}`}
          storeKey="eventOccurences"
          text="Enregistrer"
        >
          Enregistrer
        </SubmitButton>
      </td>
    </tr>
  )
}

export default compose(
  withRouter,
  connect(
    (state, ownProps) => ({
      eventOccurenceForm: selectEventOccurenceForm(state, ownProps)
    }),
    { mergeForm }
  )
)(OccurenceForm)
