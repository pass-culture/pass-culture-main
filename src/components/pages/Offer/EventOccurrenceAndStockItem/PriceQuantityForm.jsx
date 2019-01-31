import {
  assignModalConfig,
  Field,
  Form,
  Icon,
  SubmitButton,
} from 'pass-culture-shared'
import PropTypes from 'prop-types'
import React, { Component, Fragment } from 'react'
import { connect } from 'react-redux'
import { NavLink } from 'react-router-dom'
import get from 'lodash.get'
import ReactTooltip from 'react-tooltip'

const floatSep = ','

function getDisplayedPrice(value, readOnly) {
  if (value === 0) {
    if (readOnly) {
      return 'Gratuit'
    }
    return 0
  }
  if (readOnly) {
    let floatValue = value
    if (value && String(value).includes(floatSep)) {
      floatValue = parseFloat(value.replace(/,/, '.')).toFixed(2)
    }
    let floatValueString = `${floatValue} €`
    if (floatSep === ',') {
      floatValueString = floatValueString.replace('.', ',')
    }
    return floatValueString
  }

  if (value === ' ') {
    return 0
  }

  return value
}

class PriceQuantityForm extends Component {
  constructor() {
    super()
    this.isPriceInputDeactivate = false
  }

  componentDidUpdate() {
    ReactTooltip.rebuild()
  }

  handleOfferSuccessData = (state, action) => {
    const { history, offer } = this.props
    history.push(`/offres/${get(offer, 'id')}?gestion`)
  }

  onPriceBlur = event => {
    if (this.isPriceInputDeactivate) {
      return
    }

    const {
      closeInfo,
      dispatch,
      formPrice,
      hasIban,
      isStockReadOnly,
      showInfo,
    } = this.props
    if (isStockReadOnly || hasIban || !formPrice) {
      return
    }

    const priceInput = event.target
    priceInput.focus()
    this.isPriceInputDeactivate = true

    dispatch(assignModalConfig({ extraClassName: 'modal-in-modal' }))

    showInfo(
      <Fragment>
        <div className="mb12">
          Vous avez saisi une offre payante. Pensez à demander à
          l'administrateur financier nommé pour votre structure de renseigner
          son IBAN. Sans IBAN, les réservations de vos offres éligibles ne vous
          seront pas remboursées
        </div>
        <div className="has-text-centered">
          <button
            className="button is-primary"
            onClick={() => {
              dispatch(assignModalConfig({ extraClassName: null }))
              closeInfo()
              this.isPriceInputDeactivate = false
            }}>
            J'ai compris
          </button>
        </div>
      </Fragment>
    )
  }

  componentWillUnmount() {
    this.props.closeInfo()
  }

  render() {
    const {
      beginningDatetime,
      isStockReadOnly,
      isStockOnly,
      offer,
      stockFormKey,
      stockPatch,
    } = this.props

    const name = `stock${stockFormKey}`
    let action = ''
    let stockId
    if (stockPatch && stockPatch.id) {
      stockId = stockPatch.id
      action = `/stocks/${stockId}`
    } else if (stockPatch && stockPatch.id) {
      stockId = stockPatch.id
      action = `/stocks/${stockId}`
    } else if (!isStockReadOnly) {
      action = '/stocks'
      stockId = null
    }

    return (
      <Form
        action={action}
        BlockComponent={null}
        handleSuccess={this.handleOfferSuccessData}
        layout="input-only"
        name={name}
        patch={stockPatch}
        size="small"
        readOnly={isStockReadOnly}
        Tag={null}>
        <Fragment>
          <td title="Gratuit si vide">
            <Field name="eventOccurrenceId" type="hidden" />
            <Field name="offerId" type="hidden" />
            <Field
              className="input is-small input-number"
              displayValue={value => getDisplayedPrice(value, isStockReadOnly)}
              floatSep={floatSep}
              min="0"
              name="price"
              onBlur={this.onPriceBlur}
              placeholder="Gratuit"
              step="0.01"
              title="Prix"
              type={isStockReadOnly ? 'text' : 'number'}
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
              className="input is-small input-number"
              name="available"
              placeholder="Illimité"
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
              title="Places disponibles"
              type={isStockReadOnly ? 'text' : 'number'}
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
                  className="button is-secondary is-small cancel-step"
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

PriceQuantityForm.defaultProps = {
  beginninDatetime: null,
  isStockReadOnly: true,
  isStockOnly: false,
  offer: null,
  stockPatch: null,
}

PriceQuantityForm.propTypes = {
  beginningDatetime: PropTypes.string,
  closeInfo: PropTypes.func.isRequired,
  history: PropTypes.object.isRequired,
  isStockReadOnly: PropTypes.oneOfType([PropTypes.bool, PropTypes.string]),
  isStockOnly: PropTypes.bool,
  offer: PropTypes.object,
  showInfo: PropTypes.func.isRequired,
  stockPatch: PropTypes.object,
}

export default connect()(PriceQuantityForm)
