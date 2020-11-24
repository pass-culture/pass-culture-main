import React, { useCallback } from 'react'

import Icon from 'components/layout/Icon'
import { pluralize } from 'utils/pluralize'

import { isOfferFromStockProvider } from '../../domain/localProvider'

const StockSection = (props) => {
  const {
    offer,
    offerTypeType,
    stocks,
  } = props

  const textByOfferType = {
    'Event': {
      labelText: 'Dates',
      buttonText: pluralize(stocks.length, 'date'),
      modalButtonText: 'Gérer les dates et les stocks',
    },
    'Thing': {
      labelText: 'Stock',
      buttonText: pluralize(stocks.length, 'stock'),
      modalButtonText: 'Gérer les stocks',
    }
  }
  const { labelText, buttonText, modalButtonText } = textByOfferType[offerTypeType]
  const offerFromNonEditableLocalProvider = isOfferFromStockProvider(offer)

  const handleModalButtonClick = useCallback((event) => {
    event.preventDefault()
    // TODO (rlecellier): handle url changes with history
    // query.change({ gestion: '' })
  }, [])

  return (
    <div className="form-row">
      <label className="label">
        { labelText }
      </label>

      <div className="input-read-only">
        { buttonText }
      </div>

      <button
        className="button is-primary is-outlined is-small manage-stock"
        disabled={offerFromNonEditableLocalProvider ? 'disabled' : ''}
        id="manage-stocks"
        onClick={handleModalButtonClick()}
        type="button"
      >
        <span className="icon">
          <Icon svg="ico-calendar-red" />
        </span>
        <span>
          { modalButtonText }
        </span>
      </button>
    </div>
  )
}

export default StockSection
