import React, { Component, Fragment } from 'react'
import { NavLink } from 'react-router-dom'

import get from 'lodash.get'
import { Field, Form, SubmitButton } from 'pass-culture-shared'

class PriceQuantityForm extends Component {
  handleOfferSuccessData = (state, action) => {
    const { history, offer } = this.props
    history.push(`/offres/${get(offer, 'id')}?gestion`)
  }

  render() {
    const {
      offer,
      isStockOnly,
      stockPatch,
      isStockReadOnly,
      beginningDatetime,
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
        <Fragment>
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
              step="0.01"
              min="0"
              title="Prix"
            />
          </td>
          <td title="Laissez vide si pas de limite">
            <Field
              maxDate={isStockOnly ? undefined : beginningDatetime}
              name="bookingLimitDatetime"
              placeholder="Laissez vide si pas de limite"
              type="date"
            />
          </td>
          <td title="Laissez vide si pas de limite">
            <Field name="available" title="Places disponibles" type="number" />
          </td>
          {!isStockReadOnly && (
            <Fragment>
              <td>
                <SubmitButton className="button is-primary is-small submitStep">
                  Valider
                </SubmitButton>
              </td>
              <td className="is-clipped">
                <NavLink
                  className="button is-secondary is-small"
                  to={`/offres/${get(offer, 'id')}?gestion`}>
                  Annuler
                </NavLink>
              </td>
            </Fragment>
          )}
        </Fragment>
      </Form>
    )
  }
}

export default PriceQuantityForm
