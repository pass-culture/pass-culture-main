import cn from 'classnames'
import { isAfter } from 'date-fns'
import { useFormikContext } from 'formik'
import React from 'react'

import formRowStyles from 'components/StockEventFormRow/SharedStockEventFormRow.module.scss'
import { IcoEuro } from 'icons'
import { DatePicker, TextInput, TimePicker } from 'ui-kit'

import styles from './StockEventForm.module.scss'
import { IStockEventFormValues } from './types'

export interface IStockEventFormProps {
  today: Date
  stockIndex: number
}

const StockEventForm = ({
  today,
  stockIndex,
}: IStockEventFormProps): JSX.Element => {
  const { values, setFieldValue, setTouched } = useFormikContext<{
    stocks: IStockEventFormValues[]
  }>()

  const stockFormValues = values.stocks[stockIndex]
  const { readOnlyFields } = stockFormValues

  const onChangeBeginningDate = (_name: string, date: Date | null) => {
    const stockBookingLimitDatetime = stockFormValues.bookingLimitDatetime
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
        placeholder="Ex: 20€"
        disabled={readOnlyFields.includes('price')}
        rightIcon={() =>
          stockFormValues.price.toString().length > 0 ? <IcoEuro /> : <></>
        }
        type="number"
        hideHiddenFooter={true}
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
      />
    </>
  )
}

export default StockEventForm
