import moment from 'moment'
import PropTypes from 'prop-types'
import React, { Fragment, useCallback, useEffect, useState } from 'react'

import Icon from 'components/layout/Icon'
import DateInput from 'components/layout/inputs/DateInput/DateInput'
import TimeInput from 'components/layout/inputs/TimeInput/TimeInput'
import DeleteStockDialogContainer from 'components/pages/Offer/Offer/Stocks/DeleteStockDialog/DeleteStockDialogContainer'
import * as pcapi from 'repository/pcapi/pcapi'

import { validateCreatedStock, validateUpdatedStock } from './domain'

const StockItem = ({
  departmentCode,
  errors,
  isEvent,
  isNewStock,
  isOfferSynchronized,
  notifyCreateSuccess,
  notifyError,
  notifyUpdateSuccess,
  offerId,
  onChange,
  refreshOffer,
  removeStockInCreation,
  setStockErrors,
  initialStock,
  setParentIsEditing,
}) => {
  const today = new Date().toISOString()

  const [isEditing, setIsEditing] = useState(isNewStock)
  const [isDeleting, setIsDeleting] = useState(false)
  const [beginningDate, setBeginningDate] = useState(initialStock.beginningDatetime)
  const [beginningTime, setBeginningTime] = useState(initialStock.beginningDatetime)
  const [bookingLimitDatetime, setBookingLimitDatetime] = useState(
    initialStock.bookingLimitDatetime
  )
  const [price, setPrice] = useState(initialStock.price)
  const [totalQuantity, setTotalQuantity] = useState(initialStock.quantity)

  const buildBeginningDatetime = useCallback(() => {
    if (beginningDate === '') {
      return ''
    }
    const momentBeginningDate = moment(beginningDate)
    const momentBeginningTime = moment(beginningTime)

    momentBeginningDate.hours(momentBeginningTime.hours())
    momentBeginningDate.minutes(momentBeginningTime.minutes())

    return momentBeginningDate.utc().format()
  }, [beginningDate, beginningTime])

  useEffect(
    function updateStock() {
      const stock = {
        key: initialStock.key,
        beginningDatetime: buildBeginningDatetime(),
        bookingLimitDatetime,
        price,
        quantity: totalQuantity,
      }
      if (isNewStock) {
        onChange(stock)
      }
    },
    [
      beginningDate,
      bookingLimitDatetime,
      buildBeginningDatetime,
      initialStock.key,
      isNewStock,
      onChange,
      price,
      totalQuantity,
    ]
  )

  const enableUpdatableFields = useCallback(() => {
    setIsEditing(true)
  }, [])

  const refreshStock = useCallback(() => {
    setIsEditing(isNewStock)
    setBeginningDate(initialStock.beginningDatetime)
    setBeginningTime(initialStock.beginningDatetime)
    setBookingLimitDatetime(initialStock.bookingLimitDatetime)
    setPrice(initialStock.price)
    setTotalQuantity(initialStock.quantity)
  }, [isNewStock, initialStock])

  useEffect(() => refreshStock(), [refreshStock])

  useEffect(() => setParentIsEditing(isEditing), [setParentIsEditing, isEditing])

  const getSelectedDatetime = useCallback(
    momentDateTime => {
      if (momentDateTime.creationData().format === 'HH:mm') {
        const momentBeginningDatetime = moment(beginningDate)
        momentBeginningDatetime.hours(momentDateTime.hours())
        momentBeginningDatetime.minutes(momentDateTime.minutes())

        return momentBeginningDatetime.utc().format()
      }
      return momentDateTime.utc().format()
    },
    [beginningDate]
  )

  const changeBeginningDatetime = useCallback(
    momentDateTime => {
      if (momentDateTime) {
        const selectedDatetime = getSelectedDatetime(momentDateTime)
        setBeginningDate(selectedDatetime)
        bookingLimitDatetime > selectedDatetime && setBookingLimitDatetime(selectedDatetime)
      } else {
        setBeginningDate('')
      }
    },
    [bookingLimitDatetime, getSelectedDatetime]
  )

  const changeHour = useCallback(
    momentDateTime => {
      if (momentDateTime) {
        const selectedTime = getSelectedDatetime(momentDateTime)
        setBeginningTime(selectedTime)
      } else {
        setBeginningTime('')
      }
    },
    [getSelectedDatetime]
  )

  const changeBookingLimitDatetime = useCallback(momentDateTime => {
    setBookingLimitDatetime(momentDateTime ? momentDateTime.utc().format() : '')
  }, [])

  const getBookingLimitDatetimeForEvent = useCallback(() => {
    const momentBookingLimitDatetime = moment(bookingLimitDatetime)
    if (bookingLimitDatetime === '' || momentBookingLimitDatetime.isSame(beginningDate, 'day')) {
      return beginningDate
    } else {
      return momentBookingLimitDatetime.utc().endOf('day').format()
    }
  }, [bookingLimitDatetime, beginningDate])

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
  const computedRemainingQuantity = totalQuantityValue - initialStock.bookingsQuantity
  const remainingQuantityValue = totalQuantityValue !== '' ? computedRemainingQuantity : 'Illimité'
  const isEventStockEditable = beginningDate > today
  const isThingStockEditable = !isOfferSynchronized
  const isStockEditable = isEvent ? isEventStockEditable : isThingStockEditable
  const isStockDeletable = isEvent ? initialStock.isEventDeletable : !isOfferSynchronized

  useEffect(() => {
    if (Object.keys(errors).length > 0) {
      notifyError(Object.values(errors))
    }
  }, [errors, notifyError])

  const isValid = useCallback(() => {
    const stock = {
      beginningDatetime: beginningDate,
      bookingLimitDatetime,
      price,
      quantity: totalQuantity,
    }
    const stockErrors = isNewStock ? validateCreatedStock(stock) : validateUpdatedStock(stock)

    const hasErrors = Object.keys(stockErrors).length > 0

    if (hasErrors) {
      setStockErrors(initialStock.key, stockErrors)
    }

    return !hasErrors
  }, [
    beginningDate,
    bookingLimitDatetime,
    initialStock.key,
    isNewStock,
    price,
    setStockErrors,
    totalQuantity,
  ])

  const saveChanges = useCallback(() => {
    if (isValid()) {
      const payload = {
        stockId: initialStock.id,
        price: price ? price : 0,
        quantity: totalQuantity ? totalQuantity : null,
      }
      const thingPayload = {
        ...payload,
        bookingLimitDatetime: getBookingLimitDatetimeForThing(),
      }
      const eventPayload = {
        ...payload,
        beginningDatetime: buildBeginningDatetime(),
        bookingLimitDatetime: getBookingLimitDatetimeForEvent(),
      }
      pcapi
        .updateStock(isEvent ? eventPayload : thingPayload)
        .then(async () => {
          await refreshOffer()
          notifyUpdateSuccess()
        })
        .catch(errors => {
          const submitErrors = {
            global: 'Impossible de modifier le stock.',
            ...('errors' in errors ? errors.errors : []),
          }
          setStockErrors(submitErrors)
        })
    }
  }, [
    initialStock.id,
    buildBeginningDatetime,
    isEvent,
    isValid,
    getBookingLimitDatetimeForEvent,
    getBookingLimitDatetimeForThing,
    notifyUpdateSuccess,
    price,
    setStockErrors,
    totalQuantity,
    refreshOffer,
  ])

  const removeNewStockLine = useCallback(() => {
    removeStockInCreation(initialStock.key)
  }, [removeStockInCreation, initialStock.key])

  const saveNewStock = useCallback(() => {
    if (isValid()) {
      const payload = {
        offerId: offerId,
        price: price ? price : 0,
        quantity: totalQuantity ? totalQuantity : null,
      }
      const thingPayload = {
        ...payload,
        bookingLimitDatetime: getBookingLimitDatetimeForThing(),
      }
      const eventPayload = {
        ...payload,
        beginningDatetime: buildBeginningDatetime(),
        bookingLimitDatetime: getBookingLimitDatetimeForEvent(),
      }

      pcapi
        .createStock(isEvent ? eventPayload : thingPayload)
        .then(() => {
          refreshOffer()
          removeNewStockLine()
          notifyCreateSuccess()
        })
        .catch(errors => {
          const submitErrors = {
            global: 'Impossible d’ajouter le stock.',
            ...('errors' in errors ? errors.errors : []),
          }
          setStockErrors(submitErrors)
        })
    }
  }, [
    isValid,
    offerId,
    price,
    totalQuantity,
    getBookingLimitDatetimeForThing,
    buildBeginningDatetime,
    getBookingLimitDatetimeForEvent,
    isEvent,
    refreshOffer,
    removeNewStockLine,
    notifyCreateSuccess,
    setStockErrors,
  ])

  return (
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
              openingUtcDateIsoFormat={today}
              utcDateIsoFormat={beginningDate}
            />
          </td>
          <td className="small-input">
            <TimeInput
              ariaLabel="Heure de l’événement"
              departmentCode={departmentCode}
              disabled={!isEditing || isOfferSynchronized}
              onChange={changeHour}
              utcDateIsoFormat={beginningTime}
            />
          </td>
        </Fragment>
      )}
      <td className="small-input input-text">
        <input
          aria-label="Prix"
          className={`it-input ${priceValue ? 'with-euro-icon' : ''} ${
            'price' in errors ? 'error' : ''
          }`}
          disabled={!isEditing}
          name="price"
          onChange={changePrice}
          placeholder="Gratuit"
          type="number"
          value={priceValue}
        />
      </td>
      <td className={`${isEvent ? 'regular-input' : 'large-input'}`}>
        <DateInput
          ariaLabel="Date limite de réservation"
          departmentCode={departmentCode}
          disabled={!isEditing}
          maxUtcDateIsoFormat={beginningDate}
          onChange={changeBookingLimitDatetime}
          openingUtcDateIsoFormat={today}
          utcDateIsoFormat={bookingLimitDatetime}
        />
      </td>
      <td className="small-input input-text">
        <input
          aria-label="Quantité"
          className={`it-input ${'quantity' in errors ? 'error' : ''}`}
          disabled={!isEditing}
          name="quantity"
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
        {!isNewStock && initialStock.bookingsQuantity}
      </td>
      <td className="action-column">
        {!isNewStock &&
          (!isEditing ? (
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
              disabled={isEvent && (!beginningDate || !beginningTime)}
              onClick={isNewStock ? saveNewStock : saveChanges}
              type="button"
            >
              <Icon
                alt="Valider les modifications"
                svg="ico-validate-p"
              />
            </button>
          ))}
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
        {isDeleting && (
          <DeleteStockDialogContainer
            refreshOffer={refreshOffer}
            setIsDeleting={setIsDeleting}
            stockId={initialStock.id}
          />
        )}
      </td>
    </tr>
  )
}

StockItem.defaultProps = {
  errors: {},
  isNewStock: false,
  onChange: null,
  removeStockInCreation: null,
}

StockItem.propTypes = {
  departmentCode: PropTypes.string.isRequired,
  errors: PropTypes.shape(),
  initialStock: PropTypes.shape({
    id: PropTypes.string,
    key: PropTypes.string,
    bookingsQuantity: PropTypes.number,
    isEventDeletable: PropTypes.bool,
    beginningDatetime: PropTypes.string,
    bookingLimitDatetime: PropTypes.string,
    price: PropTypes.number.isRequired,
    quantity: PropTypes.number,
  }).isRequired,
  isEvent: PropTypes.bool.isRequired,
  isNewStock: PropTypes.bool,
  isOfferSynchronized: PropTypes.bool.isRequired,
  notifyCreateSuccess: PropTypes.func.isRequired,
  notifyError: PropTypes.func.isRequired,
  notifyUpdateSuccess: PropTypes.func.isRequired,
  offerId: PropTypes.string.isRequired,
  onChange: PropTypes.func,
  refreshOffer: PropTypes.func.isRequired,
  removeStockInCreation: PropTypes.func,
  setParentIsEditing: PropTypes.func.isRequired,
  setStockErrors: PropTypes.func.isRequired,
}

export default StockItem
