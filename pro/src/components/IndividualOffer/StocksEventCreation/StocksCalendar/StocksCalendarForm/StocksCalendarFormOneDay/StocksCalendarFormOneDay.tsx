import { isValid } from 'date-fns'
import { UseFormReturn } from 'react-hook-form'

import { GetIndividualOfferWithAddressResponseModel } from 'apiClient/v1'
import { StocksCalendarFormValues } from 'components/IndividualOffer/StocksEventCreation/form/types'
import { DatePicker } from 'ui-kit/form/DatePicker/DatePicker'

import { StocksCalendarFormTimeAndPrice } from '../StocksCalendarFormTimeAndPrice/StocksCalendarFormTimeAndPrice'

import styles from './StocksCalendarFormOneDay.module.scss'

export function StocksCalendarFormOneDay({
  form,
  offer,
}: {
  form: UseFormReturn<StocksCalendarFormValues>
  offer: GetIndividualOfferWithAddressResponseModel
}) {
  const date = form.watch('oneDayDate') || ''

  const isValidDate = isValid(new Date(date))

  return (
    <div className={styles['container']}>
      <DatePicker
        className={styles['date-field-layout']}
        label="Date"
        required
        minDate={new Date()}
        error={form.formState.errors.oneDayDate?.message}
        {...form.register('oneDayDate')}
      />

      {isValidDate && (
        <StocksCalendarFormTimeAndPrice form={form} offer={offer} />
      )}
    </div>
  )
}
