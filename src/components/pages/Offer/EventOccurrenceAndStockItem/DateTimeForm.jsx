import React, { Component, Fragment } from 'react'
import { NavLink } from 'react-router-dom'
import get from 'lodash.get'
import { Field, Form, SubmitButton } from 'pass-culture-shared'

class DateTimeForm extends Component {
  handleEventOccurrenceSuccessData = (state, action) => {
    const { history, offer, stockPatch } = this.props
    const {
      payload: { datum },
    } = action
    const eventOccurrenceId = datum.id
    const stockIdOrNew = get(stockPatch, 'id', 'nouveau')
    const offerId = get(offer, 'id')
    history.push(
      `/offres/${offerId}?gestion&date=${eventOccurrenceId}&stock=${stockIdOrNew}`
    )
  }

  render() {
    const {
      offer,
      eventOccurrencePatch,
      isEventOccurrenceReadOnly,
      beginningDatetime,
      eventOccurrences,
      tz,
    } = this.props

    return (
      <Form
        action={`/eventOccurrences/${get(eventOccurrencePatch, 'id', '')}`}
        BlockComponent={null}
        handleSuccess={this.handleEventOccurrenceSuccessData}
        layout="input-only"
        name={`eventOccurrence${get(eventOccurrencePatch, 'id', '')}`}
        patch={eventOccurrencePatch}
        readOnly={isEventOccurrenceReadOnly}
        size="small"
        Tag={null}>
        <td>
          <Field name="offerId" type="hidden" />
          <Field name="venueId" type="hidden" />
          <Field minDate={beginningDatetime} name="endDatetime" type="hidden" />
          <Field
            debug
            highlightedDates={eventOccurrences.map(eo => eo.beginningDatetime)}
            minDate="today"
            name="beginningDate"
            patchKey="beginningDatetime"
            readOnly={isEventOccurrenceReadOnly}
            required
            title="Date"
            type="date"
            tz={tz}
          />
        </td>
        <td>
          <Field
            name="beginningTime"
            patchKey="beginningDatetime"
            readOnly={isEventOccurrenceReadOnly}
            required
            title="Heure"
            type="time"
            tz={tz}
          />
        </td>
        <td>
          <Field
            name="endTime"
            patchKey="endDatetime"
            readOnly={isEventOccurrenceReadOnly}
            required
            title="Heure de fin"
            type="time"
            tz={tz}
          />
        </td>
        {!isEventOccurrenceReadOnly && (
          <Fragment>
            <td>
              <SubmitButton className="button is-primary is-small submitStep">
                Suivant
              </SubmitButton>
            </td>
            <td />
            <td />
            <td />
            <td className="is-clipped">
              <NavLink
                className="button is-secondary is-small cancel-step"
                to={`/offres/${get(offer, 'id')}?gestion`}>
                Annuler
              </NavLink>
            </td>
          </Fragment>
        )}
      </Form>
    )
  }
}

export default DateTimeForm
