import moment from 'moment-timezone'
import PropTypes from 'prop-types'
import React, { Fragment, useCallback, useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { v4 as generateRandomUuid } from 'uuid'

import PageTitle from 'components/layout/PageTitle/PageTitle'
import { ReactComponent as AddStockSvg } from 'icons/ico-plus.svg'
import * as pcapi from 'repository/pcapi/pcapi'
import { getDepartmentTimezone } from 'utils/timezone'

import { EVENT_CANCELLATION_INFORMATION, THING_CANCELLATION_INFORMATION } from './_constants'
import {
  createStockPayload,
  formatAndSortStocks,
  validateCreatedStock,
  validateUpdatedStock,
} from './StockItem/domain'
import StockItem from './StockItem/StockItem'

const Stocks = ({ offer, showErrorNotification, showSuccessNotification }) => {
  const offerId = offer.id
  const [isLoading, setIsLoading] = useState(true)
  const [stocks, setStocks] = useState([])
  const isOfferSynchronized = Boolean(offer.lastProvider)
  const [formErrors, setFormErrors] = useState({})

  const loadStocks = useCallback(() => {
    return pcapi.loadStocks(offerId).then(receivedStocks => {
      setStocks(formatAndSortStocks(receivedStocks.stocks))
      setIsLoading(false)
    })
  }, [offerId])

  useEffect(() => {
    moment.tz.setDefault(getDepartmentTimezone(offer.venue.departementCode))
    loadStocks()
    return () => {
      moment.tz.setDefault()
    }
  }, [loadStocks, offer.venue.departementCode])

  useEffect(() => {
    if (Object.values(formErrors).length > 0) {
      showErrorNotification()
    }
  }, [formErrors, showErrorNotification])

  const addNewStock = useCallback(() => {
    let newStock = {
      key: generateRandomUuid(),
      price: 0,
      quantity: null,
      bookingLimitDatetime: '',
    }
    if (offer.isEvent) {
      newStock.beginningDatetime = ''
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
        createStockPayload(stockInCreation, offer.isEvent)
      )
      const stocksToUpdate = updatedStocks.map(updatedStock => {
        const payload = createStockPayload(updatedStock, offer.isEvent)
        payload.id = updatedStock.id
        return payload
      })
      pcapi
        .bulkCreateOrEditStock(offer.id, [...stocksToCreate, ...stocksToUpdate])
        .then(() => {
          loadStocks()
          showSuccessNotification()
        })
        .catch(() => showErrorNotification())
    }
  }, [
    existingStocks,
    loadStocks,
    offer.isEvent,
    offer.id,
    showErrorNotification,
    showSuccessNotification,
    stocksInCreation,
  ])

  if (isLoading) {
    return null
  }

  return (
    <div className="stocks-page">
      <PageTitle title="Vos stocks" />
      <h3 className="section-title">
        {'Stock et prix'}
      </h3>

      <div className="cancellation-information">
        {offer.isEvent ? EVENT_CANCELLATION_INFORMATION : THING_CANCELLATION_INFORMATION}
      </div>
      {stocks.length === 0 ? (
        <button
          className="primary-button with-icon add-first-stock-button"
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
              disabled={hasOfferThingOneStockAlready || isOfferSynchronized}
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
                <StockItem
                  departmentCode={offer.venue.departementCode}
                  errors={formErrors[stockInCreation.key]}
                  initialStock={stockInCreation}
                  isEvent={offer.isEvent}
                  isNewStock
                  key={stockInCreation.key}
                  onChange={updateStock}
                  refreshStocks={loadStocks}
                  removeStockInCreation={removeStockInCreation}
                />
              ))}

              {existingStocks.map(stock => (
                <StockItem
                  departmentCode={offer.venue.departementCode}
                  errors={formErrors[stock.key]}
                  initialStock={stock}
                  isEvent={offer.isEvent}
                  key={stock.id}
                  lastProvider={offer.lastProvider}
                  onChange={updateStock}
                  refreshStocks={loadStocks}
                />
              ))}
            </tbody>
          </table>
          <section className="actions-section">
            <Link
              className="secondary-link"
              to={`/offres/v2/${offerId}/edition`}
            >
              {'Annuler et quitter'}
            </Link>
            <button
              className="primary-button"
              onClick={submitStocks}
              type="button"
            >
              {'Enregistrer'}
            </button>
          </section>
        </Fragment>
      )}
    </div>
  )
}

Stocks.propTypes = {
  offer: PropTypes.shape({
    id: PropTypes.string.isRequired,
  }).isRequired,
  showErrorNotification: PropTypes.func.isRequired,
  showSuccessNotification: PropTypes.func.isRequired,
}

export default Stocks
