import moment from 'moment'
import { assignModalConfig } from 'pass-culture-shared'
import PropTypes from 'prop-types'
import React, { Component, Fragment } from 'react'
import { createParseNumberValue } from 'react-final-form-utils'
import ReactTooltip from 'react-tooltip'

import {
  createFormatAvailable,
  formatPrice,
  getRemainingStocksCount,
} from '../../../utils'
import {
  DateField,
  HiddenField,
  NumberField,
} from 'components/layout/form/fields'
import Icon from './../../../../../../../layout/Icon'
import { PriceField } from '../../../../../../../layout/form/fields/PriceField'

export class ProductFields extends Component {
  static isParsedByForm = true

  constructor() {
    super()
    this.isPriceInputDeactivate = false
  }

  componentDidUpdate() {
    ReactTooltip.rebuild()
  }

  componentWillUnmount() {
    const { closeInfo } = this.props
    closeInfo()
  }

  handleOnPriceBlur = event => {
    if (this.isPriceInputDeactivate) {
      return
    }

    const { closeInfo, dispatch, hasIban, readOnly, showInfo } = this.props
    const formPrice = createParseNumberValue('number')(event.target.value)

    if (readOnly || hasIban || !formPrice) {
      return
    }

    const priceInput = event.target
    priceInput.focus()
    this.isPriceInputDeactivate = true

    dispatch(assignModalConfig({ extraClassName: 'modal-in-modal' }))

    showInfo(
      <Fragment>
        <div className="mb24 has-text-left">
          {"Vous avez saisi une offre payante. Pensez à demander à"}
          {"l'administrateur financier nommé pour votre structure de renseigner"}
          {"son IBAN. Sans IBAN, les réservations de vos offres éligibles ne vous"}
          {"seront pas remboursées."}
        </div>
        <div className="has-text-right">
          <button
            className="button is-primary"
            onClick={() => {
              dispatch(assignModalConfig({ extraClassName: null }))
              closeInfo()
              this.isPriceInputDeactivate = false
            }}
          >
            {"J'ai compris"}
          </button>
        </div>
      </Fragment>
    )
  }

  render() {
    const {
      beginningDatetime,
      isEvent,
      readOnly,
      stock,
      timezone,
      venue,
    } = this.props
    const { available, bookings } = stock || {}
    const remainingStocksCount = getRemainingStocksCount(
      available,
      bookings || []
    )

    return (
      <Fragment>
        <td title="Gratuit si vide">
          <HiddenField
            name="offerId"
            type="hidden"
          />
          <HiddenField
            name="venueId"
            type="hidden"
          />
          <PriceField
            format={formatPrice(readOnly)}
            name="price"
            onBlur={this.handleOnPriceBlur}
            placeholder="Gratuit"
            readOnly={readOnly}
            title="Prix"
          />
        </td>
        <td
          className="tooltiped"
          title="Laissez vide si pas de limite"
        >
          <DateField
            maxDate={isEvent ? moment(beginningDatetime) : undefined}
            name="bookingLimitDatetime"
            placeholder="Laissez vide si pas de limite"
            readOnly={readOnly}
            renderValue={() => {
              if (readOnly) {
                return null
              }

              let tip =
                "L'heure limite de réservation de ce jour est 23h59 et ne peut pas être changée."
              if (venue && venue.isVirtual) {
                tip = `${tip}<br /><br /> Vous êtes sur une offre numérique, la zone horaire de cette date correspond à celle de votre structure.`
              }

              return (
                <span
                  className="button tooltip tooltip-info"
                  data-place="bottom"
                  data-tip={`<p>${tip}</p>`}
                  data-type="info"
                >
                  <Icon svg="picto-info" />
                </span>
              )
            }}
            timezone={timezone}
          />
        </td>
        <td className="tooltiped">
          <NumberField
            format={createFormatAvailable()}
            name="available"
            placeholder="Illimité"
            readOnly={readOnly}
            renderValue={() => {
              if (readOnly) {
                return null
              }
              return (
                <span
                  className="button tooltip tooltip-info"
                  data-place="bottom"
                  data-tip="<p>Laissez ce champ vide pour un nombre de places ou stock illimité.</p>"
                  data-type="info"
                >
                  <Icon svg="picto-info" />
                </span>
              )
            }}
            title="Stock[ou] Places affecté[es]"
          />
        </td>

        <td
          className="is-small remaining-stock"
          id="remaining-stock"
        >
          {remainingStocksCount}
        </td>
      </Fragment>
    )
  }
}

ProductFields.defaultProps = {
  beginningDatetime: null,
  isEvent: true,
  offer: null,
  readOnly: true,
  stock: null,
  timezone: null,
}

ProductFields.propTypes = {
  beginningDatetime: PropTypes.string,
  closeInfo: PropTypes.func.isRequired,
  dispatch: PropTypes.func.isRequired,
  hasIban: PropTypes.bool.isRequired,
  isEvent: PropTypes.bool,
  offer: PropTypes.shape(),
  parseFormChild: PropTypes.func,
  readOnly: PropTypes.oneOfType([PropTypes.bool, PropTypes.string]),
  showInfo: PropTypes.func.isRequired,
  stock: PropTypes.shape(),
  timezone: PropTypes.string,
  venue: PropTypes.shape().isRequired,
}

export default ProductFields
