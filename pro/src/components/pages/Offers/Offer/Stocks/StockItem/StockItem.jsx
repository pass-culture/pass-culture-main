import { isAfter } from 'date-fns'
import PropTypes from 'prop-types'
import React, { Fragment, useCallback, useEffect, useState } from 'react'

import DateInput from 'components/layout/inputs/DateInput/DateInput'
import TimeInput from 'components/layout/inputs/TimeInput/TimeInput'
import { isAllocineProvider } from 'components/pages/Offers/domain/localProvider'
import DeleteStockDialogContainer from 'components/pages/Offers/Offer/Stocks/DeleteStockDialog/DeleteStockDialogContainer'
import {
  getMaximumBookingLimitDatetime as getMaximumBookingLimitDatetimeFromExpirationDatetime,
  hasStockBeenUpdated,
} from 'components/pages/Offers/Offer/Stocks/StockItem/domain'
import { getToday } from 'utils/date'
import { getLocalDepartementDateTimeFromUtc } from 'utils/timezone'

import ActivationCodesUploadDialog from '../ActivationCodesUploadDialog/ActivationCodesUploadDialog'
import StockItemOptionsMenu from '../StockItemOptionsMenu/StockItemOptionsMenu'

const noOperation = () => {}

const StockItem = ({
  departmentCode,
  errors,
  isDigital,
  isEvent,
  isNewStock,
  isDisabled: isOfferDisabled,
  lastProvider,
  onChange,
  onDelete,
  removeStockInCreation,
  initialStock,
}) => {
  const today = getLocalDepartementDateTimeFromUtc(getToday(), departmentCode)

  const [isDeleting, setIsDeleting] = useState(false)
  const [beginningDate, setBeginningDate] = useState(
    initialStock.beginningDatetime
  )
  const [beginningTime, setBeginningTime] = useState(
    initialStock.beginningDatetime
  )
  const [bookingLimitDatetime, setBookingLimitDatetime] = useState(
    initialStock.bookingLimitDatetime
  )
  const [price, setPrice] = useState(initialStock.price)
  const [totalQuantity, setTotalQuantity] = useState(initialStock.quantity)
  const [isActivationCodesDialogOpen, setIsActivationCodesDialogOpen] =
    useState(false)
  const [activationCodes, setActivationCodes] = useState(
    initialStock.activationCodes || []
  )
  const [
    activationCodesExpirationDatetime,
    setActivationCodesExpirationDatetime,
  ] = useState(initialStock.activationCodesExpirationDatetime)

  const hasActivationCodes = isNewStock
    ? activationCodes.length > 0
    : Boolean(initialStock.hasActivationCodes)

  useEffect(
    function updateStock() {
      const initialValues = {
        activationCodes,
        activationCodesExpirationDatetime,
        hasActivationCodes: Boolean(initialStock.hasActivationCodes),
        beginningDatetime: initialStock.beginningDatetime,
        bookingLimitDatetime: initialStock.bookingLimitDatetime,
        price: initialStock.price,
        quantity: initialStock.quantity,
      }
      let updatedStock = {
        key: initialStock.key,
        activationCodes,
        activationCodesExpirationDatetime,
        bookingLimitDatetime,
        price,
        quantity: totalQuantity,
      }
      if (isEvent) {
        updatedStock = { ...updatedStock, beginningDate, beginningTime }
      }
      if (isNewStock || hasStockBeenUpdated(initialValues, updatedStock)) {
        onChange(updatedStock)
      }
    },
    [
      activationCodes,
      activationCodesExpirationDatetime,
      beginningDate,
      beginningTime,
      bookingLimitDatetime,
      initialStock.activationCodes,
      initialStock.activationCodesExpirationDatetime,
      initialStock.hasActivationCodes,
      initialStock.beginningDatetime,
      initialStock.bookingLimitDatetime,
      initialStock.key,
      initialStock.price,
      initialStock.quantity,
      isEvent,
      isNewStock,
      onChange,
      price,
      totalQuantity,
    ]
  )

  const changeBeginningDate = useCallback(
    selectedDateTime => {
      if (selectedDateTime) {
        setBeginningDate(selectedDateTime)
        if (isAfter(bookingLimitDatetime, selectedDateTime)) {
          setBookingLimitDatetime(selectedDateTime)
        }
      } else {
        setBeginningDate(null)
      }
    },
    [bookingLimitDatetime]
  )

  const changeBeginningHour = useCallback(selectedTime => {
    if (selectedTime) {
      setBeginningTime(selectedTime)
    } else {
      setBeginningTime(null)
    }
  }, [])

  const changeBookingLimitDatetime = useCallback(
    dateTime => setBookingLimitDatetime(dateTime),
    []
  )

  const changeActivationCodesExpirationDatetime = useCallback(
    expirationDatetime => {
      setActivationCodesExpirationDatetime(expirationDatetime)
      if (expirationDatetime !== null) {
        const maximumBookingLimitDatetime =
          getMaximumBookingLimitDatetimeFromExpirationDatetime(
            expirationDatetime
          )

        if (bookingLimitDatetime === null) {
          setBookingLimitDatetime(maximumBookingLimitDatetime)
        }
      }
    },
    [bookingLimitDatetime]
  )

  const changePrice = useCallback(event => setPrice(event.target.value), [])

  const changeTotalQuantity = useCallback(
    event => setTotalQuantity(event.target.value),
    []
  )

  const askDeletionConfirmation = useCallback(() => setIsDeleting(true), [])

  const closeActivationCodesDialog = useCallback(() => {
    setIsActivationCodesDialogOpen(false)
    setActivationCodes([])
    changeActivationCodesExpirationDatetime(null)
  }, [changeActivationCodesExpirationDatetime])

  const totalQuantityValue = totalQuantity !== null ? totalQuantity : ''
  const computedRemainingQuantity =
    totalQuantityValue - initialStock.bookingsQuantity
  const remainingQuantityValue =
    totalQuantityValue !== '' ? computedRemainingQuantity : 'Illimité'
  const isEventStockEditable =
    initialStock.updated || isAfter(beginningDate, today)
  const isOfferSynchronized = lastProvider !== null
  const isOfferSynchronizedWithAllocine = isAllocineProvider(lastProvider)
  const isThingStockEditable = !isOfferSynchronized
  const isStockEditable =
    isNewStock || (isEvent ? isEventStockEditable : isThingStockEditable)
  const isStockDeletable =
    isNewStock ||
    (isEvent ? initialStock.isEventDeletable : !isOfferSynchronized)

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

  const validateActivationCodes = useCallback(activationCodes => {
    setTotalQuantity(activationCodes.length)
    setIsActivationCodesDialogOpen(false)
  }, [])

  const getMaximumBookingLimitDatetime = useCallback(() => {
    if (activationCodesExpirationDatetime !== null) {
      return getMaximumBookingLimitDatetimeFromExpirationDatetime(
        activationCodesExpirationDatetime
      )
    }

    return beginningDate
  }, [activationCodesExpirationDatetime, beginningDate])

  return (
    <tr
      data-testid={`stock-item-${initialStock.key}`}
      title={computeStockTitle()}
    >
      {isEvent && (
        <Fragment>
          <td>
            <DateInput
              ariaLabel="Date de l’évènement"
              dateTime={beginningDate}
              disabled={
                isOfferDisabled || isOfferSynchronized || !isStockEditable
              }
              inError={'beginningDate' in errors}
              minDateTime={today}
              onChange={changeBeginningDate}
              openingDateTime={today}
            />
          </td>
          <td className="resized-input">
            <TimeInput
              ariaLabel="Heure de l’évènement"
              dateTime={beginningTime}
              disabled={
                isOfferDisabled || isOfferSynchronized || !isStockEditable
              }
              inError={'beginningTime' in errors}
              onChange={changeBeginningHour}
            />
          </td>
        </Fragment>
      )}
      <td className="resized-input input-text">
        <input
          aria-label="Prix"
          className={`it-input ${price ? 'with-euro-icon' : ''} ${
            'price' in errors || 'price300' in errors ? 'error' : 'price-input'
          }`}
          disabled={
            isOfferDisabled ||
            (isOfferSynchronized && !isOfferSynchronizedWithAllocine) ||
            !isStockEditable
          }
          name="price"
          onChange={changePrice}
          placeholder="Ex : 20€"
          type="number"
          value={price}
        />
      </td>
      <td className={`${!isEvent ? 'resized-input' : ''}`}>
        <DateInput
          ariaLabel="Date limite de réservation"
          dateTime={bookingLimitDatetime}
          disabled={
            isOfferDisabled ||
            (isOfferSynchronized && !isOfferSynchronizedWithAllocine) ||
            !isStockEditable
          }
          maxDateTime={getMaximumBookingLimitDatetime()}
          onChange={changeBookingLimitDatetime}
          openingDateTime={today}
        />
      </td>
      {activationCodesExpirationDatetime && (
        <td>
          <DateInput
            ariaLabel="Date limite de validité"
            dateTime={activationCodesExpirationDatetime}
            disabled
            onChange={noOperation}
          />
        </td>
      )}
      <td className="resized-input input-text quantity-input">
        <input
          aria-label="Quantité"
          className={`it-input ${'quantity' in errors ? 'error' : ''}`}
          disabled={
            isOfferDisabled ||
            (isOfferSynchronized && !isOfferSynchronizedWithAllocine) ||
            !isStockEditable ||
            hasActivationCodes
          }
          name="quantity"
          onChange={changeTotalQuantity}
          placeholder="Illimité"
          type="number"
          value={totalQuantityValue}
        />
      </td>
      <td>{!isNewStock && remainingQuantityValue}</td>
      <td>{!isNewStock && initialStock.bookingsQuantity}</td>
      <td className="action-column">
        <StockItemOptionsMenu
          canAddActivationCodes={isDigital && !isEvent}
          deleteButtonTitle={computeStockDeleteButtonTitle()}
          deleteStock={
            isNewStock ? removeNewStockLine : askDeletionConfirmation
          }
          disableDeleteButton={
            isOfferDisabled || !isStockDeletable || isDeleting
          }
          hasActivationCodes={hasActivationCodes}
          isNewStock={isNewStock}
          isOfferDisabled={isOfferDisabled}
          setIsActivationCodesDialogOpen={setIsActivationCodesDialogOpen}
        />
        {isDeleting && (
          <DeleteStockDialogContainer
            isEvent={isEvent}
            onDelete={onDelete}
            setIsDeleting={setIsDeleting}
            stockId={initialStock.id}
          />
        )}
        {isActivationCodesDialogOpen && (
          <ActivationCodesUploadDialog
            activationCodes={activationCodes}
            activationCodesExpirationDatetime={
              activationCodesExpirationDatetime
            }
            bookingLimitDatetime={bookingLimitDatetime}
            changeActivationCodesExpirationDatetime={
              changeActivationCodesExpirationDatetime
            }
            closeDialog={closeActivationCodesDialog}
            setActivationCodes={setActivationCodes}
            today={today}
            validateActivationCodes={validateActivationCodes}
          />
        )}
      </td>
    </tr>
  )
}

StockItem.defaultProps = {
  departmentCode: '',
  errors: {},
  isDigital: false,
  isDisabled: false,
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
    hasActivationCodes: PropTypes.bool,
    activationCodes: PropTypes.arrayOf(PropTypes.string),
    activationCodesExpirationDatetime: PropTypes.instanceOf(Date),
    beginningDatetime: PropTypes.instanceOf(Date),
    bookingLimitDatetime: PropTypes.instanceOf(Date),
    price: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    quantity: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    updated: PropTypes.bool,
  }).isRequired,
  isDigital: PropTypes.bool,
  isDisabled: PropTypes.bool,
  isEvent: PropTypes.bool.isRequired,
  isNewStock: PropTypes.bool,
  lastProvider: PropTypes.shape(),
  onChange: PropTypes.func.isRequired,
  onDelete: PropTypes.func.isRequired,
  removeStockInCreation: PropTypes.func,
}

export default StockItem
