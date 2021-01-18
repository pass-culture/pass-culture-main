import moment from 'moment'
import PropTypes from 'prop-types'
import React, { Fragment, useCallback, useEffect, useState } from 'react'

import Icon from 'components/layout/Icon'
import DateInput from 'components/layout/inputs/DateInput/DateInput'
import TimeInput from 'components/layout/inputs/TimeInput/TimeInput'
import DeleteStockDialogContainer from 'components/pages/Offer/Offer/Stocks/DeleteStockDialog/DeleteStockDialogContainer'
import * as pcapi from 'repository/pcapi/pcapi'

const StockItem = ({
  departmentCode,
  isEvent,
  isNewStock,
  isOfferSynchronized,
  notifyCreateSuccess,
  notifyError,
  notifyUpdateSuccess,
  offerId,
  refreshOffer,
  stock,
  setIsAddingNewStock,
  setParentIsEditing,
}) => {
  const today = new Date().toISOString()

  const [formErrors, setFormErrors] = useState({})
  const [isEditing, setIsEditing] = useState(isNewStock)
  const [isDeleting, setIsDeleting] = useState(false)
  const [beginningDatetime, setBeginningDatetime] = useState(stock.beginningDatetime)
  const [beginningTime, setBeginningTime] = useState(stock.beginningDatetime)
  const [bookingLimitDatetime, setBookingLimitDatetime] = useState(stock.bookingLimitDatetime)
  const [price, setPrice] = useState(stock.price)
  const [totalQuantity, setTotalQuantity] = useState(stock.quantity)

  const enableUpdatableFields = useCallback(() => {
    setIsEditing(true)
  }, [])

  const refreshStock = useCallback(() => {
    setIsEditing(isNewStock)
    setBeginningDatetime(stock.beginningDatetime)
    setBeginningTime(stock.beginningDatetime)
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

  useEffect(() => {
    const errorMessages = Object.values(formErrors)
    if (errorMessages.length > 0) {
      notifyError(errorMessages)
    }
  }, [formErrors, notifyError])

  const isValid = useCallback(() => {
    let errors = []

    if (price < 0) {
      errors['price'] = 'Le prix doit être positif.'
    }

    if (totalQuantity < 0) {
      errors['quantity'] = 'La quantité doit être positive.'
    }

    if (!isNewStock && remainingQuantityValue < 0) {
      const missingQuantityMessage =
        'La quantité ne peut être inférieure au nombre de réservations.'
      if ('quantity' in errors) {
        errors['quantity'] = `${errors['quantity']}\n${missingQuantityMessage}`
      } else {
        errors['quantity'] = missingQuantityMessage
      }
    }

    const hasErrors = Object.values(errors).length > 0

    if (hasErrors) {
      const formErrors = {
        global: isNewStock ? 'Impossible d’ajouter le stock.' : 'Impossible de modifier le stock.',
        ...errors,
      }
      setFormErrors(formErrors)
    }

    return !hasErrors
  }, [isNewStock, price, remainingQuantityValue, setFormErrors, totalQuantity])

  const buildBeginningDatetime = useCallback(() => {
    const momentBeginningDate = moment(beginningDatetime)
    const momentBeginningTime = moment(beginningTime)

    momentBeginningDate.hours(momentBeginningTime.hours())
    momentBeginningDate.minutes(momentBeginningTime.minutes())

    return momentBeginningDate.utc().format()
  }, [beginningDatetime, beginningTime])

  const saveChanges = useCallback(() => {
    if (isValid()) {
      const payload = {
        stockId: stock.id,
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
          setFormErrors(submitErrors)
        })
    }
  }, [
    stock.id,
    buildBeginningDatetime,
    isEvent,
    isValid,
    getBookingLimitDatetimeForEvent,
    getBookingLimitDatetimeForThing,
    notifyUpdateSuccess,
    price,
    setFormErrors,
    totalQuantity,
    refreshOffer,
  ])

  const removeNewStockLine = useCallback(() => {
    setIsAddingNewStock(false)
  }, [setIsAddingNewStock])

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
          setFormErrors(submitErrors)
        })
    }
  }, [
    offerId,
    buildBeginningDatetime,
    isEvent,
    getBookingLimitDatetimeForEvent,
    getBookingLimitDatetimeForThing,
    isValid,
    notifyCreateSuccess,
    price,
    setFormErrors,
    totalQuantity,
    refreshOffer,
    removeNewStockLine,
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
              stock={stock}
              utcDateIsoFormat={beginningDatetime}
            />
          </td>
          <td className="small-input">
            <TimeInput
              ariaLabel="Heure de l’événement"
              departmentCode={departmentCode}
              disabled={!isEditing || isOfferSynchronized}
              onChange={changeHour}
              stock={stock}
              utcDateIsoFormat={beginningTime}
            />
          </td>
        </Fragment>
      )}
      <td className="small-input input-text">
        <input
          aria-label="Prix"
          className={`it-input ${priceValue ? 'with-euro-icon' : ''} ${
            'price' in formErrors ? 'error' : ''
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
          maxUtcDateIsoFormat={beginningDatetime}
          onChange={changeBookingLimitDatetime}
          openingUtcDateIsoFormat={today}
          stock={stock}
          utcDateIsoFormat={bookingLimitDatetime}
        />
      </td>
      <td className="small-input input-text">
        <input
          aria-label="Quantité"
          className={`it-input ${'quantity' in formErrors ? 'error' : ''}`}
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
            disabled={isEvent && (!beginningDatetime || !beginningTime)}
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
        {isDeleting && (
          <DeleteStockDialogContainer
            refreshOffer={refreshOffer}
            setIsDeleting={setIsDeleting}
            stockId={stock.id}
          />
        )}
      </td>
    </tr>
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
  notifyCreateSuccess: PropTypes.func.isRequired,
  notifyError: PropTypes.func.isRequired,
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
