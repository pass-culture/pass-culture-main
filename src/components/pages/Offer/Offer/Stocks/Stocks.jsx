import moment from 'moment-timezone'
import PropTypes from 'prop-types'
import React, { Fragment, useCallback, useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { v4 as generateRandomUuid } from 'uuid'

import Icon from 'components/layout/Icon'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import * as pcapi from 'repository/pcapi/pcapi'
import { getDepartmentTimezone } from 'utils/timezone'

import { EVENT_CANCELLATION_INFORMATION, THING_CANCELLATION_INFORMATION } from './_constants'
import { validateCreatedStock, validateUpdatedStock } from './StockItem/domain'
import StockItemContainer from './StockItem/StockItemContainer'

const getBookingLimitDatetimeForEvent = stock => {
  const momentBookingLimitDatetime = moment(stock.bookingLimitDatetime)
  if (
    stock.bookingLimitDatetime === '' ||
    momentBookingLimitDatetime.isSame(stock.beginningDatetime, 'day')
  ) {
    return stock.beginningDatetime
  } else {
    return momentBookingLimitDatetime.utc().endOf('day').format()
  }
}

const getBookingLimitDatetimeForThing = stock => {
  if (stock.bookingLimitDatetime) {
    return moment(stock.bookingLimitDatetime).utc().endOf('day').format()
  }
  return null
}

const Stocks = ({ offer, showErrorNotification, showSuccessNotification }) => {
  const offerId = offer.id
  const [stocks, setStocks] = useState([])
  const [departmentCode, setDepartmentCode] = useState(null)
  const [isEvent, setIsEvent] = useState(false)
  const [isEditing, setIsEditing] = useState(false)
  const [isOfferSynchronized, setIsOfferSynchronized] = useState(false)
  const [formErrors, setFormErrors] = useState({})

  useEffect(() => {
    moment.tz.setDefault(getDepartmentTimezone(departmentCode))

    return () => {
      moment.tz.setDefault()
    }
  }, [departmentCode])

  const getOffer = useCallback(() => {
    return pcapi.loadOffer(offerId).then(offer => {
      const stocksByDescendingBeginningDatetime = offer.stocks
        .map(stock => ({ ...stock, key: stock.id }))
        .sort(
          (stock1, stock2) =>
            moment(stock2.beginningDatetime).unix() - moment(stock1.beginningDatetime).unix()
        )
      setIsEvent(offer.isEvent)
      setIsOfferSynchronized(Boolean(offer.lastProviderId))
      setDepartmentCode(offer.venue.departementCode)
      setStocks(stocksByDescendingBeginningDatetime)
    })
  }, [offerId])

  useEffect(() => {
    getOffer()
  }, [getOffer])

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
    if (isEvent) {
      newStock.beginningDatetime = ''
    }
    setStocks(currentStocks => [newStock, ...currentStocks])
  }, [isEvent])

  const removeStockInCreation = useCallback(
    key => setStocks(currentStocks => currentStocks.filter(stock => stock.key !== key)),
    []
  )

  const hasOfferThingOneStockAlready = !isEvent && stocks.length > 0
  const existingStocks = useMemo(() => stocks.filter(stock => stock.id !== undefined), [stocks])
  const stocksInCreation = useMemo(() => stocks.filter(stock => stock.id === undefined), [stocks])

  const setStockErrors = useCallback((key, errors) => {
    setFormErrors({
      global: 'Une ou plusieurs erreurs sont présentes dans le formulaire.',
      [key]: errors,
    })
  }, [])

  const updateStock = useCallback(updatedStockValues => {
    setStocks(currentStocks => {
      const stockToUpdateIndex = currentStocks.findIndex(
        currentStock => currentStock.key === updatedStockValues.key
      )
      const updatedStock = { ...currentStocks[stockToUpdateIndex], ...updatedStockValues }
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
    }

    return !hasErrors
  }

  const submitStocks = useCallback(() => {
    if (areValid(stocksInCreation)) {
      const stocksToCreate = stocksInCreation.map(stockInCreation => {
        let payload = {
          price: stockInCreation.price ? stockInCreation.price : 0,
          quantity: stockInCreation.quantity ? stockInCreation.quantity : null,
        }
        if (isEvent) {
          payload.beginningDatetime = stockInCreation.beginningDatetime
          payload.bookingLimitDatetime = getBookingLimitDatetimeForEvent(stockInCreation)
        } else {
          payload.bookingLimitDatetime = getBookingLimitDatetimeForThing(stockInCreation)
        }
        return payload
      })
      pcapi
        .bulkCreateOrEditStock(offer.id, stocksToCreate)
        .then(() => {
          getOffer()
          showSuccessNotification()
        })
        .catch(() => showErrorNotification())
    }
  }, [
    isEvent,
    getOffer,
    offer.id,
    showErrorNotification,
    showSuccessNotification,
    stocksInCreation,
  ])

  return (
    <div className="stocks-page">
      <PageTitle title="Vos stocks" />
      <h3 className="section-title">
        {'Stock et prix'}
      </h3>

      <div className="cancellation-information">
        {isEvent ? EVENT_CANCELLATION_INFORMATION : THING_CANCELLATION_INFORMATION}
      </div>
      <button
        className="tertiary-button"
        disabled={hasOfferThingOneStockAlready || isOfferSynchronized}
        onClick={addNewStock}
        type="button"
      >
        <Icon svg="ico-plus" />
        {isEvent ? 'Ajouter une date' : 'Ajouter un stock'}
      </button>
      <table>
        <thead>
          <tr>
            {isEvent && (
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
            <th>
              {'Stock restant'}
            </th>
            <th>
              {'Réservations'}
            </th>
            <th className="action-column">
              {isEditing ? 'Valider' : 'Modifier'}
            </th>
            <th className="action-column">
              {isEditing ? 'Annuler' : 'Supprimer'}
            </th>
          </tr>
        </thead>
        <tbody>
          {stocksInCreation.map(stockInCreation => (
            <StockItemContainer
              departmentCode={departmentCode}
              errors={formErrors[stockInCreation.key]}
              initialStock={stockInCreation}
              isEvent={isEvent}
              isNewStock
              isOfferSynchronized={isOfferSynchronized}
              key={stockInCreation.key}
              offerId={offerId}
              onChange={updateStock}
              refreshOffer={getOffer}
              removeStockInCreation={removeStockInCreation}
              setParentIsEditing={setIsEditing}
              setStockErrors={setStockErrors}
            />
          ))}

          {existingStocks.map(stock => (
            <StockItemContainer
              departmentCode={departmentCode}
              errors={formErrors[stock.key]}
              initialStock={stock}
              isEvent={isEvent}
              isOfferSynchronized={isOfferSynchronized}
              key={stock.id}
              offerId={offerId}
              refreshOffer={getOffer}
              setParentIsEditing={setIsEditing}
              setStockErrors={setStockErrors}
            />
          ))}
        </tbody>
      </table>
      <section className="actions-section">
        <Link
          className="secondary-link"
          to="/offres/"
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
