import get from 'lodash.get'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import FormField from './layout/FormField'
import Label from './layout/Label'
import SubmitButton from './layout/SubmitButton'
import { NEW } from '../utils/config'

import Icon from './layout/Icon'
import { SingleDatePicker } from 'react-dates'

class OccurenceForm extends Component {

  componentDidUpdate () {
    /*
    console.log('date', date)
    if (!time) {
      console.warn('You need to define a time first')
      return
    }

    const [hours, minutes] = time.split(':')
    const value = date.clone().hour(hours).minute(minutes)

    // check that it does not match already an occurence
    const alreadySelectedDate = availableDates && availableDates.find(o =>
      availableDates.isSame(value))
    if (alreadySelectedDate) {
      return
    }
    */
  }

  render () {
    const {
      match: { params: { occasionId } },
      id,
      isNew,
      offer,
      time
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
            time={time}
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

export default compose(
  withRouter,
  connect(
    state => ({
      time: get(state, `form.${NEW}.time`)
    })
  )
)(OccurenceForm)
