import {
  assignModalConfig,
  Field,
  Icon,
  recursiveMap,
} from 'pass-culture-shared'
import PropTypes from 'prop-types'
import React, { Component, Fragment } from 'react'
import ReactTooltip from 'react-tooltip'

import { FLOATSEP, getDisplayedPrice, getRemainingStock } from './utils'

export class EventOrThingFields extends Component {
  constructor() {
    super()
    this.isPriceInputDeactivate = false
  }

  componentDidUpdate() {
    ReactTooltip.rebuild()
  }

  componentWillUnmount() {
    this.props.closeInfo()
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
      isReadOnly,
      showInfo,
    } = this.props
    if (isReadOnly || hasIban || !formPrice) {
      return
    }

    const priceInput = event.target
    priceInput.focus()
    this.isPriceInputDeactivate = true

    dispatch(assignModalConfig({ extraClassName: 'modal-in-modal' }))

    showInfo(
      <Fragment>
        <div className="mb24 has-text-left">
          Vous avez saisi une offre payante. Pensez à demander à
          l'administrateur financier nommé pour votre structure de renseigner
          son IBAN. Sans IBAN, les réservations de vos offres éligibles ne vous
          seront pas remboursées.
        </div>
        <div className="has-text-right">
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

  render() {
    const {
      beginningDatetime,
      isReadOnly,
      isEventStock,
      parseFormChild,
      stockPatch,
    } = this.props
    const { available, bookings } = stockPatch || {}
    const remainingStock = getRemainingStock(available, bookings || [])

    const children = (
      <Fragment>
        <td title="Gratuit si vide">
          <Field name="offerId" type="hidden" />
          <Field name="venueId" type="hidden" />
          <Field
            className="input is-small input-number"
            displayValue={value => getDisplayedPrice(value, isReadOnly)}
            floatSep={FLOATSEP}
            min="0"
            name="price"
            onBlur={this.onPriceBlur}
            placeholder="Gratuit"
            step="0.01"
            title="Prix"
            type={isReadOnly ? 'text' : 'number'}
          />
        </td>
        <td title="Laissez vide si pas de limite">
          <Field
            maxDate={isEventStock ? beginningDatetime : undefined}
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
              if (!isReadOnly) {
                return (
                  <span
                    className="button tooltip qty-info"
                    data-place="bottom"
                    data-tip="<p>Laissez ce champ vide pour un nombre de places ou stock illimité.</p>"
                    data-type="info">
                    <Icon svg="picto-info" />
                  </span>
                )
              }
            }}
            title="Stock[ou] Places affecté[es]"
            type={isReadOnly ? 'text' : 'number'}
          />
        </td>

        <td className="is-small remaining-stock" id="remaining-stock">
          {remainingStock}
        </td>
      </Fragment>
    )
    return recursiveMap(children, parseFormChild)
  }
}

EventOrThingFields.defaultProps = {
  beginningDatetime: null,
  isReadOnly: true,
  isEventStock: true,
  offer: null,
  parseFormChild: c => c,
  stockPatch: null,
}

EventOrThingFields.propTypes = {
  beginningDatetime: PropTypes.string,
  closeInfo: PropTypes.func.isRequired,
  dispatch: PropTypes.func.isRequired,
  isReadOnly: PropTypes.oneOfType([PropTypes.bool, PropTypes.string]),
  isEventStock: PropTypes.bool,
  offer: PropTypes.object,
  parseFormChild: PropTypes.func,
  showInfo: PropTypes.func.isRequired,
  stockPatch: PropTypes.object,
}

export default EventOrThingFields
EventOrThingFields.isParsedByForm = true
