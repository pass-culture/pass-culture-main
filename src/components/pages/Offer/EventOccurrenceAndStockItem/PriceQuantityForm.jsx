import React, { Component, Fragment } from 'react'
import { NavLink } from 'react-router-dom'
import get from 'lodash.get'
import ReactTooltip from 'react-tooltip'
import { Field, Form, SubmitButton, Icon } from 'pass-culture-shared'

class PriceQuantityForm extends Component {
  handleOfferSuccessData = (state, action) => {
    const { history, offer } = this.props
    history.push(`/offres/${get(offer, 'id')}?gestion`)
  }

  componentDidUpdate() {
    ReactTooltip.rebuild()
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
              type={isStockReadOnly ? 'text' : 'number'}
              step="0.01"
              min="0"
              title="Prix"
              className="input is-small input-number"
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
          <td className="tooltiped">
            <Field
              name="available"
              title="Places disponibles"
              type={isStockReadOnly ? 'text' : 'number'}
              placeholder="Illimité"
              className="input is-small input-number"
              renderInfo={() => {
                if (!isStockReadOnly) {
                  return (
                    <span
                      className="button tooltip qty-info"
                      data-place="bottom"
                      data-tip="<p>Laissez ce champ vide pour un nombre de places illimité.</p>"
                      data-type="info">
                      <Icon svg="picto-info" />
                    </span>
                  )
                }
              }}
            />
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
