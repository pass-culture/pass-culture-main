import React, { Component } from 'react'
import { Portal } from 'react-portal'
import get from 'lodash.get'
import { Field, Form, SubmitButton } from 'pass-culture-shared'

class CommonForm extends Component {
  handleOfferSuccessData = (state, action) => {
    const { history, offer } = this.props
    history.push(`/offres/${get(offer, 'id')}?gestion`)
  }

  render() {
    const {
      stockPatch,
      isStockReadOnly,
      beginningDatetime,
      submit,
    } = this.props

    return (
      <Form
        action={`/stocks/${get(stockPatch, 'id', '')}`}
        BlockComponent={null}
        handleSuccess={this.handleOfferSuccessData}
        layout="input-only"
        key={1}
        name={`stock${get(stockPatch, 'id', '')}`}
        patch={stockPatch}
        size="small"
        readOnly={isStockReadOnly}
        Tag={null}>
        <td title="Vide si gratuit">
          <Field name="eventOccurrenceId" type="hidden" />
          <Field name="offerId" type="hidden" />
          <Field
            displayValue={(value, { readOnly }) =>
              value === 0
                ? readOnly
                  ? 'Gratuit'
                  : 0
                : readOnly
                  ? `${value}€`
                  : value
            }
            name="price"
            placeholder="Gratuit"
            type="number"
            title="Prix"
          />
        </td>
        <td title="Laissez vide si pas de limite">
          <Field
            maxDate={beginningDatetime}
            name="bookingLimitDatetime"
            placeholder="Laissez vide si pas de limite"
            type="date"
          />
        </td>
        <td title="Laissez vide si pas de limite">
          <Field name="available" title="Places disponibles" type="number" />
        </td>
        {!isStockReadOnly && (
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

export default CommonForm
