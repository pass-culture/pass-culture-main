import get from 'lodash.get'
import React, { Component } from 'react'
import { withRouter } from 'react-router'

import FormField from './layout/FormField'
import Label from './layout/Label'
import SubmitButton from './layout/SubmitButton'
import { NEW } from '../utils/config'

class OccurenceForm extends Component {
  render () {
    const {
      match: { params: { occasionId } },
      id,
      isNew,
      offer
    } = this.props
    return (
      <tr>
        <td>
          <FormField
            collectionName="dates"
            entityId={id}
            label={<Label title="Date :" />}
            name="date"
            required
            type="date"
          />
        </td>
        <td>
          <FormField
            collectionName="dates"
            entityId={id}
            label={<Label title="Heure :" />}
            name="time"
            required
            type="time"
          />
        </td>
        <td>
          <FormField
            collectionName="offers"
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
            collectionName="offers"
            entityId={get(offer, 'id')}
            label={<Label title="Nombre de places" />}
            min={0}
            name="groupSize"
            placeholder="Laissez vide si pas de limite"
            type="number"
          />
        </td>
        <td>
          <FormField
            collectionName="offers"
            entityId={get(offer, 'id')}
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
              const eo = get(form, `eventOccurencesById.${isNew ? NEW : id}`)

              const [hours, minutes] = eo.time.split(':')
              const beginningDatetime = eo.date.clone().hour(hours).minute(minutes)

              return Object.assign({
                beginningDatetime,
                eventId: occasionId
              }, eo)
            }}
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
}

export default withRouter(OccurenceForm)
