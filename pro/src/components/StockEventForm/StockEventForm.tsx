import cn from 'classnames'
import { isAfter } from 'date-fns'
import { useFormikContext } from 'formik'
import React from 'react'

import formRowStyles from 'components/StockEventFormRow/SharedStockEventFormRow.module.scss'
import { OFFER_WIZARD_MODE } from 'core/Offers'
import { SelectOption } from 'custom_types/form'
import { useOfferWizardMode } from 'hooks'
import useActiveFeature from 'hooks/useActiveFeature'
import { EuroIcon } from 'icons'
import { DatePicker, TextInput, TimePicker, Select } from 'ui-kit'

import { STOCK_EVENT_EDITION_EMPTY_SYNCHRONIZED_READ_ONLY_FIELDS } from './constants'
import styles from './StockEventForm.module.scss'
import { IStockEventFormValues } from './types'

export interface IStockEventFormProps {
  today: Date
  stockIndex: number
  disableAllStockFields?: boolean
  priceCategoriesOptions: SelectOption[]
}

const StockEventForm = ({
  today,
  stockIndex,
  disableAllStockFields = false,
  priceCategoriesOptions,
}: IStockEventFormProps): JSX.Element => {
  const { values, setFieldValue, setTouched } = useFormikContext<{
    stocks: IStockEventFormValues[]
  }>()
  const mode = useOfferWizardMode()
  const isPriceCategoriesActive = useActiveFeature(
    'WIP_ENABLE_MULTI_PRICE_STOCKS'
  )

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

      {isPriceCategoriesActive ? (
        <Select
          name={`stocks[${stockIndex}]priceCategoryId`}
          options={priceCategoriesOptions}
          smallLabel
          label="Tarif"
          isLabelHidden={stockIndex !== 0}
          className={cn(
            styles['input-price-category'],
            styles['field-layout-align-self']
          )}
          classNameLabel={formRowStyles['field-layout-label']}
          classNameFooter={styles['field-layout-footer']}
          defaultOption={{
            label: 'Séléctionner un tarif',
            value: '',
          }}
          disabled={priceCategoriesOptions.length === 1}
        />
      ) : (
        <TextInput
          smallLabel
          name={`stocks[${stockIndex}]price`}
          label="Tarif"
          isLabelHidden={stockIndex !== 0}
          className={cn(
            styles['input-price'],
            styles['field-layout-align-self']
          )}
          classNameLabel={formRowStyles['field-layout-label']}
          classNameFooter={styles['field-layout-footer']}
          disabled={readOnlyFields.includes('price')}
          rightIcon={() => <EuroIcon />}
          type="number"
          step="0.01"
          hideHiddenFooter={true}
          data-testid="input-price"
        />
      )}

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
        name={`stocks[${stockIndex}]remainingQuantity`}
        label={
          mode === OFFER_WIZARD_MODE.EDITION ? 'Quantité restante' : 'Quantité'
        }
        isLabelHidden={stockIndex !== 0}
        placeholder="Illimité"
        className={cn(
          styles['input-quantity'],
          styles['field-layout-align-self']
        )}
        classNameLabel={formRowStyles['field-layout-label']}
        classNameFooter={styles['field-layout-footer']}
        disabled={readOnlyFields.includes('remainingQuantity')}
        type="number"
        hasDecimal={false}
        hideHiddenFooter={true}
      />
    </>
  )
}

export default StockEventForm
