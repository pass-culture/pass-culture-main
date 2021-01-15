import moment from 'moment-timezone'
import PropTypes from 'prop-types'
import React, { Fragment, useCallback, useEffect, useState } from 'react'

import Icon from 'components/layout/Icon'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import * as pcapi from 'repository/pcapi/pcapi'
import { getDepartmentTimezone } from 'utils/timezone'

import { EVENT_CANCELLATION_INFORMATION, THING_CANCELLATION_INFORMATION } from './_constants'
import StockItemContainer from './StockItem/StockItemContainer'

const Stocks = ({ offer }) => {
  const offerId = offer.id
  const [stocks, setStocks] = useState([])
  const [departmentCode, setDepartmentCode] = useState(null)
  const [isEvent, setIsEvent] = useState(false)
  const [isEditing, setIsEditing] = useState(false)
  const [isAddingNewStock, setIsAddingNewStock] = useState(false)
  const [isOfferSynchronized, setIsOfferSynchronized] = useState(false)

  useEffect(() => {
    moment.tz.setDefault(getDepartmentTimezone(departmentCode))

    return () => {
      moment.tz.setDefault()
    }
  }, [departmentCode])

  const getOffer = useCallback(() => {
    return pcapi.loadOffer(offerId).then(offer => {
      const stocksByDescendingBeginningDatetime = offer.stocks.sort(
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

  const addNewStock = useCallback(() => {
    setIsAddingNewStock(true)
  }, [setIsAddingNewStock])

  const hasOfferThingOneStockAlready = !isEvent && stocks.length > 0

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
        disabled={isAddingNewStock || hasOfferThingOneStockAlready || isOfferSynchronized}
        onClick={addNewStock}
        title={isAddingNewStock ? 'Vous ne pouvez ajouter qu’un stock à la fois.' : ''}
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
          {isAddingNewStock && (
            <StockItemContainer
              departmentCode={departmentCode}
              isEvent={isEvent}
              isNewStock
              isOfferSynchronized={isOfferSynchronized}
              offerId={offerId}
              refreshOffer={getOffer}
              setIsAddingNewStock={setIsAddingNewStock}
              setParentIsEditing={setIsEditing}
            />
          )}
          {stocks.map(stock => (
            <StockItemContainer
              departmentCode={departmentCode}
              isEvent={isEvent}
              isOfferSynchronized={isOfferSynchronized}
              key={stock.id}
              offerId={offerId}
              refreshOffer={getOffer}
              setIsAddingNewStock={setIsAddingNewStock}
              setParentIsEditing={setIsEditing}
              stock={stock}
            />
          ))}
        </tbody>
      </table>
    </div>
  )
}

Stocks.propTypes = {
  offer: PropTypes.shape({
    id: PropTypes.string.isRequired,
  }).isRequired,
}

export default Stocks
