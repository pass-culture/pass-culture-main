import moment from 'moment'
import PropTypes from 'prop-types'
import React, { Fragment, useCallback, useEffect, useState } from 'react'

import Icon from 'components/layout/Icon'
import { DateInput } from 'components/layout/inputs/DateInput/DateInput'
import { TimeInput } from 'components/layout/inputs/TimeInput/TimeInput'
import { DeleteStockConfirmation } from 'components/pages/Offer/Stocks/DeleteStockConfirmation/DeleteStockConfirmation'
import * as pcapi from 'repository/pcapi/pcapi'

const StockItem = ({
  departmentCode,
  isEvent,
  isNewStock,
  isOfferSynchronized,
  notifyUpdateError,
  notifyUpdateSuccess,
  offerId,
  refreshOffer,
  stock,
  setIsAddingNewStock,
  setParentIsEditing,
}) => {
  const today = new Date().toISOString()

  const [isEditing, setIsEditing] = useState(isNewStock)
  const [isDeleting, setIsDeleting] = useState(false)
  const [beginningDatetime, setBeginningDatetime] = useState(stock.beginningDatetime)
  const [bookingLimitDatetime, setBookingLimitDatetime] = useState(stock.bookingLimitDatetime)
  const [price, setPrice] = useState(stock.price)
  const [totalQuantity, setTotalQuantity] = useState(stock.quantity)

  const enableUpdatableFields = useCallback(() => {
    setIsEditing(true)
  }, [])

  const refreshStock = useCallback(() => {
    setIsEditing(isNewStock)
    setBeginningDatetime(stock.beginningDatetime)
    setBookingLimitDatetime(stock.bookingLimitDatetime)
    setPrice(stock.price)
    setTotalQuantity(stock.quantity)
  }, [isNewStock, stock])

  useEffect(() => {
    refreshStock()
  }, [refreshStock])

  useEffect(() => {
    setParentIsEditing(isEditing)
  }, [setParentIsEditing, isEditing])

  const getSelectedDatetime = useCallback(
    momentDateTime => {
      if (momentDateTime.creationData().format === 'HH:mm') {
        const momentBeginningDatetime = moment(beginningDatetime)
        momentBeginningDatetime.hours(momentDateTime.hours())
        momentBeginningDatetime.minutes(momentDateTime.minutes())

        return momentBeginningDatetime.utc().format()
      }
      return momentDateTime.utc().format()
    },
    [beginningDatetime]
  )

  const changeBeginningDatetime = useCallback(
    momentDateTime => {
      if (momentDateTime) {
        const selectedDatetime = getSelectedDatetime(momentDateTime)
        setBeginningDatetime(selectedDatetime)
        bookingLimitDatetime > selectedDatetime && setBookingLimitDatetime(selectedDatetime)
      } else {
        setBeginningDatetime('')
      }
    },
    [bookingLimitDatetime, getSelectedDatetime]
  )

  const changeBookingLimitDatetime = useCallback(momentDateTime => {
    const utcDateIsoFormat = momentDateTime ? momentDateTime.utc().format() : ''
    setBookingLimitDatetime(utcDateIsoFormat)
  }, [])

  const getBookingLimitDatetimeForEvent = useCallback(() => {
    const momentBookingLimitDatetime = moment(bookingLimitDatetime)
    if (
      bookingLimitDatetime === '' ||
      momentBookingLimitDatetime.isSame(beginningDatetime, 'day')
    ) {
      return beginningDatetime
    } else {
      return momentBookingLimitDatetime.utc().endOf('day').format()
    }
  }, [bookingLimitDatetime, beginningDatetime])

  const getBookingLimitDatetimeForThing = useCallback(() => {
    if (bookingLimitDatetime) {
      return moment(bookingLimitDatetime).utc().endOf('day').format()
    }
    return null
  }, [bookingLimitDatetime])

  const changePrice = useCallback(event => setPrice(event.target.value), [])

  const changeTotalQuantity = useCallback(event => setTotalQuantity(event.target.value), [])

  const askDeletionConfirmation = useCallback(() => {
    setIsDeleting(true)
  }, [])

  const priceValue = price !== 0 ? price : ''
  const totalQuantityValue = totalQuantity !== null ? totalQuantity : ''
  const computedRemainingQuantity = totalQuantityValue - stock.bookingsQuantity
  const remainingQuantityValue = totalQuantityValue !== '' ? computedRemainingQuantity : 'Illimité'
  const isEventStockEditable = beginningDatetime > today
  const isThingStockEditable = !isOfferSynchronized
  const isStockEditable = isEvent ? isEventStockEditable : isThingStockEditable
  const isStockDeletable = isEvent ? stock.isEventDeletable : !isOfferSynchronized

  const saveChanges = useCallback(() => {
    const payload = {
      id: stock.id,
      price: price ? price : 0,
      quantity: totalQuantity ? totalQuantity : null,
    }
    const thingPayload = {
      ...payload,
      bookingLimitDatetime: getBookingLimitDatetimeForThing(),
    }
    const eventPayload = {
      ...payload,
      beginningDatetime: beginningDatetime,
      bookingLimitDatetime: getBookingLimitDatetimeForEvent(),
    }
    pcapi
      .updateStock(isEvent ? eventPayload : thingPayload)
      .then(async () => {
        await refreshOffer()
        notifyUpdateSuccess()
      })
      .catch(() => {
        notifyUpdateError()
      })
  }, [
    stock.id,
    beginningDatetime,
    isEvent,
    getBookingLimitDatetimeForEvent,
    getBookingLimitDatetimeForThing,
    notifyUpdateError,
    notifyUpdateSuccess,
    price,
    totalQuantity,
    refreshOffer,
  ])

  const removeNewStockLine = useCallback(() => {
    setIsAddingNewStock(false)
  }, [setIsAddingNewStock])

  const saveNewStock = useCallback(() => {
    pcapi
      .createStock({
        offerId: offerId,
        beginningDatetime: beginningDatetime,
        bookingLimitDatetime: getBookingLimitDatetimeForEvent(),
        price: price ? price : 0,
        quantity: totalQuantity ? totalQuantity : null,
      })
      .then(() => {
        refreshOffer()
        removeNewStockLine()
      })
  }, [
    offerId,
    beginningDatetime,
    getBookingLimitDatetimeForEvent,
    price,
    totalQuantity,
    refreshOffer,
    removeNewStockLine,
  ])

  return (
    <Fragment>
      <tr>
        {isEvent && (
          <Fragment>
            <td className="regular-input">
              <DateInput
                ariaLabel="Date de l’événement"
                departmentCode={departmentCode}
                disabled={!isEditing || isOfferSynchronized}
                minUtcDateIsoFormat={today}
                onChange={changeBeginningDatetime}
                stock={stock}
                utcDateIsoFormat={beginningDatetime}
              />
            </td>
            <td className="small-input">
              <TimeInput
                ariaLabel="Heure de l’événement"
                departmentCode={departmentCode}
                disabled={!isEditing || isOfferSynchronized}
                onChange={changeBeginningDatetime}
                stock={stock}
                utcDateIsoFormat={beginningDatetime}
              />
            </td>
          </Fragment>
        )}
        <td className="small-input input-text">
          <input
            aria-label="Prix"
            className={`it-input ${priceValue ? 'with-euro-icon' : ''}`}
            disabled={!isEditing}
            onChange={changePrice}
            placeholder="Gratuit"
            type="number"
            value={priceValue}
          />
        </td>
        <td className="regular-input">
          <DateInput
            ariaLabel="Date limite de réservation"
            departmentCode={departmentCode}
            disabled={!isEditing}
            maxUtcDateIsoFormat={beginningDatetime}
            onChange={changeBookingLimitDatetime}
            stock={stock}
            utcDateIsoFormat={bookingLimitDatetime}
          />
        </td>
        <td className="small-input input-text">
          <input
            aria-label="Quantité"
            className="it-input"
            disabled={!isEditing}
            onChange={changeTotalQuantity}
            placeholder="Illimité"
            type="number"
            value={totalQuantityValue}
          />
        </td>
        <td>
          {!isNewStock && remainingQuantityValue}
        </td>
        <td>
          {!isNewStock && stock.bookingsQuantity}
        </td>
        <td className="action-column">
          {!isEditing ? (
            <button
              className="secondary-button"
              disabled={!isStockEditable || isDeleting}
              onClick={enableUpdatableFields}
              type="button"
            >
              <Icon
                alt="Modifier le stock"
                svg="ico-pen"
              />
            </button>
          ) : (
            <button
              className="secondary-button validate-button"
              disabled={isEvent && !beginningDatetime}
              onClick={isNewStock ? saveNewStock : saveChanges}
              type="button"
            >
              <Icon
                alt="Valider les modifications"
                svg="ico-validate-p"
              />
            </button>
          )}
        </td>
        <td className="action-column">
          {!isEditing ? (
            <button
              className="secondary-button"
              disabled={!isStockDeletable || isDeleting}
              onClick={askDeletionConfirmation}
              type="button"
            >
              <Icon
                alt="Supprimer le stock"
                svg="ico-close-r"
              />
            </button>
          ) : (
            <button
              className="secondary-button"
              onClick={isNewStock ? removeNewStockLine : refreshStock}
              type="button"
            >
              <Icon
                alt="Annuler les modifications"
                svg="ico-back"
              />
            </button>
          )}
        </td>
      </tr>
      {isDeleting && (
        <DeleteStockConfirmation
          isEvent={isEvent}
          refreshOffer={refreshOffer}
          setIsDeleting={setIsDeleting}
          stockId={stock.id}
        />
      )}
    </Fragment>
  )
}

StockItem.defaultProps = {
  isNewStock: false,
  stock: {
    id: '',
    bookingsQuantity: 0,
    isEventDeletable: false,
    beginningDatetime: '',
    bookingLimitDatetime: '',
    price: 0,
    quantity: null,
  },
}

StockItem.propTypes = {
  departmentCode: PropTypes.string.isRequired,
  isEvent: PropTypes.bool.isRequired,
  isNewStock: PropTypes.bool,
  isOfferSynchronized: PropTypes.bool.isRequired,
  notifyUpdateError: PropTypes.func.isRequired,
  notifyUpdateSuccess: PropTypes.func.isRequired,
  offerId: PropTypes.string.isRequired,
  refreshOffer: PropTypes.func.isRequired,
  setIsAddingNewStock: PropTypes.func.isRequired,
  setParentIsEditing: PropTypes.func.isRequired,
  stock: PropTypes.shape({
    id: PropTypes.string.isRequired,
    bookingsQuantity: PropTypes.number.isRequired,
    isEventDeletable: PropTypes.bool.isRequired,
    beginningDatetime: PropTypes.string,
    bookingLimitDatetime: PropTypes.string,
    price: PropTypes.number.isRequired,
    quantity: PropTypes.number,
  }),
}

export default StockItem
