import PropTypes from 'prop-types'
import React, { Fragment, useCallback, useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { v4 as generateRandomUuid } from 'uuid'

import PageTitle from 'components/layout/PageTitle/PageTitle'
import { isOfferDisabled } from 'components/pages/Offers/domain/isOfferDisabled'
import OfferStatusBanner from 'components/pages/Offers/Offer/OfferDetails/OfferStatusBanner/OfferStatusBanner'
import {
  DIGITAL_CANCELLATION_INFORMATION,
  EVENT_CANCELLATION_INFORMATION,
  THING_CANCELLATION_INFORMATION,
} from 'components/pages/Offers/Offer/Stocks/_constants'
import {
  createStockPayload,
  formatAndSortStocks,
  validateCreatedStock,
  validateUpdatedStock,
} from 'components/pages/Offers/Offer/Stocks/StockItem/domain'
import StockItemContainer from 'components/pages/Offers/Offer/Stocks/StockItem/StockItemContainer'
import { OFFER_STATUS_DRAFT } from 'components/pages/Offers/Offers/_constants'
import { ReactComponent as AddStockSvg } from 'icons/ico-plus.svg'
import * as pcapi from 'repository/pcapi/pcapi'

const EMPTY_STRING_VALUE = ''

const Stocks = ({
  history,
  offer,
  showErrorNotification,
  showSuccessNotification,
  showSuccessNotificationStocksAndOffer,
  reloadOffer,
  autoActivateDigitalBookings,
}) => {
  const offerId = offer.id
  const [isLoading, setIsLoading] = useState(true)
  const [stocks, setStocks] = useState([])
  const isOfferSynchronized = Boolean(offer.lastProvider)
  const [formErrors, setFormErrors] = useState({})
  const isOfferDraft = offer.status === OFFER_STATUS_DRAFT
  const editionOfferLink = `/offres/${offerId}/edition`

  const loadStocks = useCallback(
    (keepCreationStocks = false) => {
      return pcapi.loadStocks(offerId).then(receivedStocks => {
        setStocks(oldStocks => {
          const stocksOnCreation = keepCreationStocks ? oldStocks.filter(stock => !stock.id) : []
          return [
            ...stocksOnCreation,
            ...formatAndSortStocks(receivedStocks.stocks, offer.venue.departementCode),
          ]
        })
        setIsLoading(false)
      })
    },
    [offerId, offer.venue.departementCode]
  )

  const onDelete = useCallback(() => {
    reloadOffer()
    loadStocks(true)
  }, [loadStocks, reloadOffer])

  useEffect(() => {
    loadStocks()
  }, [loadStocks])

  useEffect(() => {
    if (Object.values(formErrors).length > 0) {
      showErrorNotification()
    }
  }, [formErrors, showErrorNotification])

  const addNewStock = useCallback(() => {
    let newStock = {
      key: generateRandomUuid(),
      price: EMPTY_STRING_VALUE,
      quantity: null,
      bookingLimitDatetime: null,
    }
    if (offer.isEvent) {
      newStock.beginningDatetime = null
    }
    setStocks(currentStocks => [newStock, ...currentStocks])
  }, [offer.isEvent])

  const removeStockInCreation = useCallback(
    key => setStocks(currentStocks => currentStocks.filter(stock => stock.key !== key)),
    []
  )

  const hasOfferThingOneStockAlready = !offer.isEvent && stocks.length > 0
  const existingStocks = useMemo(() => stocks.filter(stock => stock.id !== undefined), [stocks])
  const stocksInCreation = useMemo(() => stocks.filter(stock => stock.id === undefined), [stocks])

  const updateStock = useCallback(updatedStockValues => {
    setStocks(currentStocks => {
      const stockToUpdateIndex = currentStocks.findIndex(
        currentStock => currentStock.key === updatedStockValues.key
      )
      const updatedStock = {
        ...currentStocks[stockToUpdateIndex],
        ...updatedStockValues,
        updated: true,
      }
      let newStocks = [...currentStocks]
      newStocks.splice(stockToUpdateIndex, 1, updatedStock)
      return newStocks
    })
  }, [])

  const areValid = stocks => {
    const stocksErrors = stocks.reduce((stocksErrors, stock) => {
      const isNewStock = stock.id === undefined
      const stockErrors = isNewStock ? validateCreatedStock(stock) : validateUpdatedStock(stock)
      const stockHasErrors = Object.keys(stockErrors).length > 0
      return stockHasErrors ? { ...stocksErrors, [stock.key]: stockErrors } : stocksErrors
    }, {})

    const hasErrors = Object.values(stocksErrors).length > 0

    if (hasErrors) {
      const formErrors = {
        global: 'Une ou plusieurs erreurs sont présentes dans le formulaire.',
        ...stocksErrors,
      }
      setFormErrors(formErrors)
    } else {
      setFormErrors({})
    }

    return !hasErrors
  }

  const submitStocks = useCallback(() => {
    const updatedStocks = existingStocks.filter(stock => stock.updated)
    if (areValid([...stocksInCreation, ...updatedStocks])) {
      const stocksToCreate = stocksInCreation.map(stockInCreation =>
        createStockPayload(stockInCreation, offer.isEvent, offer.venue.departementCode)
      )
      const stocksToUpdate = updatedStocks.map(updatedStock => {
        const payload = createStockPayload(updatedStock, offer.isEvent, offer.venue.departementCode)
        payload.id = updatedStock.id
        return payload
      })
      pcapi
        .bulkCreateOrEditStock(offer.id, [...stocksToCreate, ...stocksToUpdate])
        .then(() => {
          loadStocks()
          reloadOffer()
          isOfferDraft ? showSuccessNotificationStocksAndOffer() : showSuccessNotification()
          if (offer.status === OFFER_STATUS_DRAFT) {
            history.push(`/offres/${offer.id}/confirmation`)
          }
        })
        .catch(() => showErrorNotification())
    }
  }, [
    existingStocks,
    history,
    stocksInCreation,
    offer.id,
    offer.isEvent,
    isOfferDraft,
    offer.status,
    offer.venue.departementCode,
    loadStocks,
    reloadOffer,
    showSuccessNotification,
    showSuccessNotificationStocksAndOffer,
    showErrorNotification,
  ])

  if (isLoading) {
    return null
  }

  const isDisabled = offer.status ? isOfferDisabled(offer.status) : false
  const hasNoStock = stocks.length === 0
  const hasAtLeastOneStock = stocks.length > 0

  return (
    <div className="stocks-page">
      <PageTitle title="Vos stocks" />

      {isDisabled && <OfferStatusBanner status={offer.status} />}

      <h3 className="section-title">
        {'Stock et prix'}
      </h3>

      <div className="cancellation-information">
        {autoActivateDigitalBookings &&
          (offer.isDigital
            ? DIGITAL_CANCELLATION_INFORMATION
            : offer.isEvent
              ? EVENT_CANCELLATION_INFORMATION
              : THING_CANCELLATION_INFORMATION)}
        {!autoActivateDigitalBookings &&
          (offer.isEvent ? EVENT_CANCELLATION_INFORMATION : THING_CANCELLATION_INFORMATION)}
      </div>
      {hasNoStock ? (
        <button
          className="primary-button with-icon add-first-stock-button"
          disabled={isDisabled}
          onClick={addNewStock}
          type="button"
        >
          <AddStockSvg />
          {offer.isEvent ? 'Ajouter une date' : 'Ajouter un stock'}
        </button>
      ) : (
        <Fragment>
          {offer.isEvent && (
            <button
              className="tertiary-button with-icon"
              disabled={isDisabled || hasOfferThingOneStockAlready || isOfferSynchronized}
              onClick={addNewStock}
              type="button"
            >
              <AddStockSvg />
              {'Ajouter une date'}
            </button>
          )}
          <table>
            <thead>
              <tr>
                {offer.isEvent && (
                  <Fragment>
                    <th>
                      {'Date'}
                    </th>
                    <th>
                      {'Horaire'}
                    </th>
                  </Fragment>
                )}
                <th>
                  {'Prix'}
                </th>
                <th>
                  {'Date limite de réservation'}
                </th>
                <th>
                  {'Quantité'}
                </th>
                {(stocksInCreation.length === 0 || existingStocks.length > 0) && (
                  <Fragment>
                    <th>
                      {'Stock restant'}
                    </th>
                    <th>
                      {'Réservations'}
                    </th>
                  </Fragment>
                )}
                <th className="action-column" />
              </tr>
            </thead>
            <tbody>
              {stocksInCreation.map(stockInCreation => (
                <StockItemContainer
                  departmentCode={offer.venue.departementCode}
                  errors={formErrors[stockInCreation.key]}
                  initialStock={stockInCreation}
                  isDigital={offer.isDigital}
                  isEvent={offer.isEvent}
                  isNewStock
                  key={stockInCreation.key}
                  onChange={updateStock}
                  onDelete={onDelete}
                  removeStockInCreation={removeStockInCreation}
                />
              ))}

              {existingStocks.map(stock => (
                <StockItemContainer
                  departmentCode={offer.venue.departementCode}
                  errors={formErrors[stock.key]}
                  initialStock={stock}
                  isDigital={offer.isDigital}
                  isDisabled={isDisabled}
                  isEvent={offer.isEvent}
                  key={stock.id}
                  lastProvider={offer.lastProvider}
                  onChange={updateStock}
                  onDelete={onDelete}
                />
              ))}
            </tbody>
          </table>
        </Fragment>
      )}
      {(isOfferDraft || hasAtLeastOneStock) && (
        <Fragment>
          <div className="interval cover" />
          <div className="interval shadow" />
          <section className="actions-section">
            {!isOfferDraft && (
              <Link
                className="secondary-link"
                to={editionOfferLink}
              >
                {'Annuler et quitter'}
              </Link>
            )}
            <button
              className="primary-button"
              disabled={isDisabled || hasNoStock}
              onClick={submitStocks}
              type="button"
            >
              {isOfferDraft ? 'Valider et créer l’offre' : 'Enregistrer'}
            </button>
          </section>
        </Fragment>
      )}
    </div>
  )
}

Stocks.propTypes = {
  autoActivateDigitalBookings: PropTypes.bool.isRequired,
  history: PropTypes.shape().isRequired,
  offer: PropTypes.shape().isRequired,
  reloadOffer: PropTypes.func.isRequired,
  showErrorNotification: PropTypes.func.isRequired,
  showSuccessNotification: PropTypes.func.isRequired,
  showSuccessNotificationStocksAndOffer: PropTypes.func.isRequired,
}

export default Stocks
