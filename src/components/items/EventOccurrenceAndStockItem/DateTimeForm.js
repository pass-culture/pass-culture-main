import React, { Component } from 'react'
import { Portal } from 'react-portal'
import get from 'lodash.get'
import { Field, Form, SubmitButton } from 'pass-culture-shared'

class DateTimeForm extends Component {
  handleEventOccurrenceSuccessData = (state, action) => {
    const { history, offer, stockPatch } = this.props
    const stockIdOrNew = get(stockPatch, 'id', 'nouveau')
    history.push(
      `/offres/${get(offer, 'id')}?gestion&date=${
        action.data.id
      }&stock=${stockIdOrNew}`
    )
  }

  render() {
    const {
      eventOccurrencePatch,
      isEventOccurrenceReadOnly,
      beginningDatetime,
      eventOccurrences,
      tz,
      submit,
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
          <Portal node={submit}>
            <SubmitButton className="button is-primary is-small">
              Valider
            </SubmitButton>
          </Portal>
        )}
      </Form>
    )
  }
}

export default DateTimeForm
