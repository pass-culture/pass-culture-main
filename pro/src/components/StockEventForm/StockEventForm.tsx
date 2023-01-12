import cn from 'classnames'
import { isAfter } from 'date-fns'
import { useFormikContext } from 'formik'
import React from 'react'

import formRowStyles from 'components/StockEventFormRow/SharedStockEventFormRow.module.scss'
import { IcoEuro } from 'icons'
import { DatePicker, TextInput, TimePicker } from 'ui-kit'

import { STOCK_EVENT_EDITION_EMPTY_SYNCHRONIZED_READ_ONLY_FIELDS } from './constants'
import styles from './StockEventForm.module.scss'
import { IStockEventFormValues } from './types'

export interface IStockEventFormProps {
  today: Date
  stockIndex: number
  disableAllStockFields?: boolean
}

const StockEventForm = ({
  today,
  stockIndex,
  disableAllStockFields = false,
}: IStockEventFormProps): JSX.Element => {
  const { values, setFieldValue, setTouched } = useFormikContext<{
    stocks: IStockEventFormValues[]
  }>()

  const stockFormValues = values.stocks[stockIndex]

  if (disableAllStockFields) {
    stockFormValues.readOnlyFields =
      STOCK_EVENT_EDITION_EMPTY_SYNCHRONIZED_READ_ONLY_FIELDS
  }
  const { readOnlyFields } = stockFormValues

  const onChangeBeginningDate = (_name: string, date: Date | null) => {
    const stockBookingLimitDatetime = stockFormValues.bookingLimitDatetime
    /* istanbul ignore next: DEBT to fix */
    if (stockBookingLimitDatetime === null) {
      return
    }
    // tested but coverage don't see it.
    /* istanbul ignore next */
    if (date && isAfter(stockBookingLimitDatetime, date)) {
      setTouched({
        [`stocks[${stockIndex}]bookingLimitDatetime`]: true,
      })
      setFieldValue(`stocks[${stockIndex}]bookingLimitDatetime`, date)
    }
  }

  const onChangeQuantity = (event: React.ChangeEvent<HTMLInputElement>) => {
    const quantity = event.target.value
    let remainingQuantity: number | string =
      Number(quantity || 0) - Number(stockFormValues.bookingsQuantity || 0)

    if (quantity === '') {
      remainingQuantity = 'unlimited'
    }

    setFieldValue(`stocks[${stockIndex}]remainingQuantity`, remainingQuantity)
    setFieldValue(`stocks[${stockIndex}]quantity`, quantity)
  }

  const beginningDate = stockFormValues.beginningDate

  return (
    <>
      <DatePicker
        smallLabel
        name={`stocks[${stockIndex}]beginningDate`}
        label="Date"
        isLabelHidden={stockIndex !== 0}
        className={cn(styles['field-layout-align-self'], styles['input-date'])}
        classNameLabel={formRowStyles['field-layout-label']}
        classNameFooter={styles['field-layout-footer']}
        minDateTime={today}
        openingDateTime={today}
        disabled={readOnlyFields.includes('beginningDate')}
        onChange={onChangeBeginningDate}
        hideHiddenFooter={true}
      />
      <TimePicker
        smallLabel
        label="Horaire"
        isLabelHidden={stockIndex !== 0}
        className={cn(
          styles['input-beginning-time'],
          styles['field-layout-align-self']
        )}
        classNameLabel={formRowStyles['field-layout-label']}
        classNameFooter={styles['field-layout-footer']}
        name={`stocks[${stockIndex}]beginningTime`}
        disabled={readOnlyFields.includes('beginningTime')}
        hideHiddenFooter={true}
      />
      <TextInput
        smallLabel
        name={`stocks[${stockIndex}]price`}
        label="Prix"
        isLabelHidden={stockIndex !== 0}
        className={cn(styles['input-price'], styles['field-layout-align-self'])}
        classNameLabel={formRowStyles['field-layout-label']}
        classNameFooter={styles['field-layout-footer']}
        disabled={readOnlyFields.includes('price')}
        rightIcon={() => <IcoEuro />}
        type="number"
        step="0.01"
        hideHiddenFooter={true}
        data-testid="input-price"
      />
      <DatePicker
        smallLabel
        name={`stocks[${stockIndex}]bookingLimitDatetime`}
        label="Date limite de réservation"
        isLabelHidden={stockIndex !== 0}
        className={cn(
          styles['input-booking-limit-datetime'],
          styles['field-layout-align-self']
        )}
        classNameLabel={formRowStyles['field-layout-label']}
        classNameFooter={styles['field-layout-footer']}
        minDateTime={today}
        maxDateTime={beginningDate ? beginningDate : undefined}
        openingDateTime={today}
        disabled={readOnlyFields.includes('bookingLimitDatetime')}
        hideHiddenFooter={true}
      />
      <TextInput
        smallLabel
        name={`stocks[${stockIndex}]quantity`}
        label="Quantité"
        isLabelHidden={stockIndex !== 0}
        placeholder="Illimité"
        className={cn(
          styles['input-quantity'],
          styles['field-layout-align-self']
        )}
        classNameLabel={formRowStyles['field-layout-label']}
        classNameFooter={styles['field-layout-footer']}
        disabled={readOnlyFields.includes('quantity')}
        type="number"
        hasDecimal={false}
        hideHiddenFooter={true}
        onChange={onChangeQuantity}
      />
    </>
  )
}

export default StockEventForm
