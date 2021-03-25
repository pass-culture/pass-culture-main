/* eslint-disable react/prop-types */
import PropTypes from 'prop-types'
import React, { Fragment, useCallback, useEffect, useState } from 'react'

import DateInput from 'components/layout/inputs/DateInput/DateInput'
import TimeInput from 'components/layout/inputs/TimeInput/TimeInput'
import { isAllocineProvider } from 'components/pages/Offers/domain/localProvider'
import DeleteStockDialogContainer from 'components/pages/Offers/Offer/Stocks/DeleteStockDialog/DeleteStockDialogContainer'
import { getToday } from 'utils/date'

import { ReactComponent as DeleteStockIcon } from './assets/delete-stock.svg'
import { hasStockBeenUpdated } from './domain'

const StockItem = ({
  departmentCode,
  errors,
  isEvent,
  isNewStock,
  lastProvider,
  onChange,
  onDelete,
  removeStockInCreation,
  initialStock,
}) => {
  const today = getToday().toISOString()

  const [isDeleting, setIsDeleting] = useState(false)
  const [beginningDate, setBeginningDate] = useState(initialStock.beginningDatetime)
  const [beginningTime, setBeginningTime] = useState(initialStock.beginningDatetime)
  const [bookingLimitDatetime, setBookingLimitDatetime] = useState(
    initialStock.bookingLimitDatetime
  )
  const [price, setPrice] = useState(initialStock.price)
  const [totalQuantity, setTotalQuantity] = useState(initialStock.quantity)

  useEffect(
    function updateStock() {
      const initialValues = {
        beginningDatetime: initialStock.beginningDatetime,
        bookingLimitDatetime: initialStock.bookingLimitDatetime,
        price: initialStock.price,
        quantity: initialStock.quantity,
      }
      const updatedStock = {
        key: initialStock.key,
        beginningDate,
        beginningTime,
        bookingLimitDatetime,
        price,
        quantity: totalQuantity,
      }
      if (hasStockBeenUpdated(initialValues, updatedStock)) {
        onChange(updatedStock)
      }
    },
    [
      beginningDate,
      beginningTime,
      bookingLimitDatetime,
      initialStock.beginningDatetime,
      initialStock.bookingLimitDatetime,
      initialStock.key,
      initialStock.price,
      initialStock.quantity,
      onChange,
      price,
      totalQuantity,
    ]
  )

  const getSelectedDatetime = useCallback(dateTime => (dateTime ? dateTime.toISOString() : ''), [])

  const changeBeginningDate = useCallback(
    dateTime => {
      if (dateTime) {
        const selectedDatetime = getSelectedDatetime(dateTime)
        setBeginningDate(selectedDatetime)
        if (bookingLimitDatetime > selectedDatetime) {
          setBookingLimitDatetime(selectedDatetime)
        }
      } else {
        setBeginningDate('')
      }
    },
    [bookingLimitDatetime, getSelectedDatetime]
  )

  const changeBeginningHour = useCallback(
    dateTime => {
      if (dateTime) {
        const selectedTime = getSelectedDatetime(dateTime)
        setBeginningTime(selectedTime)
      } else {
        setBeginningTime('')
      }
    },
    [getSelectedDatetime]
  )

  const changeBookingLimitDatetime = useCallback(
    dateTime => setBookingLimitDatetime(dateTime ? dateTime.toISOString() : ''),
    []
  )

  const changePrice = useCallback(event => setPrice(event.target.value), [])

  const changeTotalQuantity = useCallback(event => setTotalQuantity(event.target.value), [])

  const askDeletionConfirmation = useCallback(() => setIsDeleting(true), [])

  const priceValue = price !== 0 ? price : ''
  const totalQuantityValue = totalQuantity !== null ? totalQuantity : ''
  const computedRemainingQuantity = totalQuantityValue - initialStock.bookingsQuantity
  const remainingQuantityValue = totalQuantityValue !== '' ? computedRemainingQuantity : 'Illimité'
  const isEventStockEditable = initialStock.updated || beginningDate > today
  const isOfferSynchronized = lastProvider !== null
  const isOfferSynchronizedWithAllocine = isAllocineProvider(lastProvider)
  const isThingStockEditable = !isOfferSynchronized
  const isStockEditable = isNewStock || (isEvent ? isEventStockEditable : isThingStockEditable)
  const isStockDeletable =
    isNewStock || (isEvent ? initialStock.isEventDeletable : !isOfferSynchronized)

  const computeStockTitle = useCallback(() => {
    if (initialStock.id && !isEventStockEditable) {
      return 'Les évènements passés ne sont pas modifiables'
    }
  }, [isEventStockEditable, initialStock.id])

  const computeStockDeleteButtonTitle = useCallback(() => {
    if (isStockDeletable) {
      return 'Supprimer le stock'
    }

    return isOfferSynchronized
      ? 'Les stock synchronisés ne peuvent être supprimés'
      : 'Les évènements terminés depuis plus de 48h ne peuvent être supprimés'
  }, [isStockDeletable, isOfferSynchronized])

  const removeNewStockLine = useCallback(() => {
    removeStockInCreation(initialStock.key)
  }, [removeStockInCreation, initialStock.key])

  return (
    <tr
      data-testid={`stock-item-${initialStock.key}`}
      title={computeStockTitle()}
    >
      {isEvent && (
        <Fragment>
          <td>
            <DateInput
              ariaLabel="Date de l’événement"
              departmentCode={departmentCode}
              disabled={isOfferSynchronized || !isStockEditable}
              inError={'beginningDate' in errors}
              minUtcDateIsoFormat={today}
              onChange={changeBeginningDate}
              openingUtcDateIsoFormat={today}
              utcDateIsoFormat={beginningDate}
            />
          </td>
          <td className="resized-input">
            <TimeInput
              ariaLabel="Heure de l’événement"
              departmentCode={departmentCode}
              disabled={isOfferSynchronized || !isStockEditable}
              inError={'beginningTime' in errors}
              onChange={changeBeginningHour}
              utcDateIsoFormat={beginningTime}
            />
          </td>
        </Fragment>
      )}
      <td className="resized-input input-text">
        <input
          aria-label="Prix"
          className={`it-input ${priceValue ? 'with-euro-icon' : ''} ${
            'price' in errors ? 'error' : ''
          }`}
          disabled={(isOfferSynchronized && !isOfferSynchronizedWithAllocine) || !isStockEditable}
          name="price"
          onChange={changePrice}
          placeholder="Gratuit"
          type="number"
          value={priceValue}
        />
      </td>
      <td className={`${!isEvent ? 'resized-input' : ''}`}>
        <DateInput
          ariaLabel="Date limite de réservation"
          departmentCode={departmentCode}
          disabled={(isOfferSynchronized && !isOfferSynchronizedWithAllocine) || !isStockEditable}
          maxUtcDateIsoFormat={beginningDate}
          onChange={changeBookingLimitDatetime}
          openingUtcDateIsoFormat={today}
          utcDateIsoFormat={bookingLimitDatetime}
        />
      </td>
      <td className="resized-input input-text">
        <input
          aria-label="Quantité"
          className={`it-input ${'quantity' in errors ? 'error' : ''}`}
          disabled={(isOfferSynchronized && !isOfferSynchronizedWithAllocine) || !isStockEditable}
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
        <button
          className="tertiary-button"
          data-testid="stock-delete-button"
          disabled={!isStockDeletable || isDeleting}
          onClick={isNewStock ? removeNewStockLine : askDeletionConfirmation}
          title={computeStockDeleteButtonTitle()}
          type="button"
        >
          <DeleteStockIcon alt="Supprimer le stock" />
        </button>
        {isDeleting && (
          <DeleteStockDialogContainer
            onDelete={onDelete}
            setIsDeleting={setIsDeleting}
            stockId={initialStock.id}
          />
        )}
      </td>
    </tr>
  )
}

StockItem.defaultProps = {
  departmentCode: '',
  errors: {},
  isNewStock: false,
  lastProvider: null,
  removeStockInCreation: null,
}

StockItem.propTypes = {
  departmentCode: PropTypes.string,
  errors: PropTypes.shape(),
  initialStock: PropTypes.shape({
    id: PropTypes.string,
    key: PropTypes.string,
    bookingsQuantity: PropTypes.number,
    isEventDeletable: PropTypes.bool,
    beginningDatetime: PropTypes.string,
    bookingLimitDatetime: PropTypes.string,
    price: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
    quantity: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  }).isRequired,
  isEvent: PropTypes.bool.isRequired,
  isNewStock: PropTypes.bool,
  lastProvider: PropTypes.shape(),
  onChange: PropTypes.func.isRequired,
  onDelete: PropTypes.func.isRequired,
  removeStockInCreation: PropTypes.func,
}

export default StockItem
