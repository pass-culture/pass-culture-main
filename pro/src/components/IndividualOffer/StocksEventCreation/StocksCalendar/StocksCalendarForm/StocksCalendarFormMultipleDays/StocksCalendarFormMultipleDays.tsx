import { addMonths, isBefore, isValid } from 'date-fns'
import { useEffect } from 'react'
import { UseFormReturn } from 'react-hook-form'

import { GetIndividualOfferWithAddressResponseModel } from 'apiClient/v1'
import { useIndividualOfferContext } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { weekDays } from 'components/IndividualOffer/StocksEventCreation/form/constants'
import { StocksCalendarFormValues } from 'components/IndividualOffer/StocksEventCreation/form/types'
import { Checkbox } from 'ui-kit/formV2/Checkbox/Checkbox'
import { DatePicker } from 'ui-kit/formV2/DatePicker/DatePicker'

import { getWeekDaysInBetweenDates } from '../../utils'
import { StocksCalendarFormTimeAndPrice } from '../StocksCalendarFormTimeAndPrice/StocksCalendarFormTimeAndPrice'

import styles from './StocksCalendarFormMultipleDays.module.scss'
import { StocksCalendarFormMultipleDaysWeekDays } from './StocksCalendarFormMultipleDaysWeekDays/StocksCalendarFormMultipleDaysWeekDays'

export function StocksCalendarFormMultipleDays({
  form,
  offer,
}: {
  form: UseFormReturn<StocksCalendarFormValues>
  offer: GetIndividualOfferWithAddressResponseModel
}) {
  const startDate = form.watch('multipleDaysStartDate') || ''
  const endDate = form.watch('multipleDaysEndDate') || ''

  const hasEndDateOrNeverEnds =
    isValid(new Date(startDate)) &&
    (form.watch('multipleDaysHasNoEndDate') ||
      (isValid(new Date(endDate)) &&
        !isBefore(new Date(endDate), new Date(startDate))))

  const hasAtLEastOneWeekDaySelected = form
    .watch('multipleDaysWeekDays')
    .find((d) => d.checked)

  const { subCategories } = useIndividualOfferContext()

  const canHaveNoEndDate = subCategories.find(
    (cat) => cat.id === offer.subcategoryId
  )?.canHaveOpeningHours

  useEffect(() => {
    //  When the selected dates change, update the checked weekdays
    const subscription = form.watch((value, { name }) => {
      if (name === 'multipleDaysStartDate' || name === 'multipleDaysEndDate') {
        const start = value.multipleDaysStartDate
          ? new Date(value.multipleDaysStartDate)
          : null
        const end = value.multipleDaysEndDate
          ? new Date(value.multipleDaysEndDate)
          : null
        const weekDaysInBetween =
          start && end ? getWeekDaysInBetweenDates(start, end) : []

        setTimeout(async () => {
          form.setValue(
            'multipleDaysWeekDays',
            weekDays.map((d) => ({
              ...d,
              //  If there is no end date, all week days are intially checked
              checked: end
                ? weekDaysInBetween.some(
                    (dInBetween) => dInBetween.value === d.value
                  )
                : true,
            }))
          )
          await form.trigger('multipleDaysWeekDays')
        })
      }
    })
    return () => subscription.unsubscribe()
  }, [form, form.watch])

  const selectedStartDate = form.watch('multipleDaysStartDate')

  return (
    <div className={styles['container']}>
      <div className={styles['dates-row']}>
        <DatePicker
          className={styles['date-field-layout']}
          label="Date de début"
          required
          minDate={new Date()}
          error={form.formState.errors.multipleDaysStartDate?.message}
          {...form.register('multipleDaysStartDate')}
        />

        <DatePicker
          className={styles['date-field-layout']}
          label="Date de fin"
          required={!form.watch('multipleDaysHasNoEndDate')}
          minDate={new Date()}
          maxDate={
            selectedStartDate
              ? addMonths(new Date(selectedStartDate), 12)
              : undefined
          }
          error={
            form.watch('multipleDaysHasNoEndDate')
              ? undefined
              : form.formState.errors.multipleDaysEndDate?.message
          }
          {...form.register('multipleDaysEndDate')}
          disabled={form.watch('multipleDaysHasNoEndDate')}
        />

        {canHaveNoEndDate && (
          <Checkbox
            label="Pas de date de fin"
            className={styles['checkbox-field-layout']}
            {...form.register('multipleDaysHasNoEndDate')}
            onChange={async (e) => {
              form.setValue('multipleDaysEndDate', undefined)
              await form.register('multipleDaysHasNoEndDate').onChange(e)
            }}
          />
        )}
      </div>

      {hasEndDateOrNeverEnds && (
        <>
          <div className={styles['week-days']}>
            <StocksCalendarFormMultipleDaysWeekDays form={form} />
          </div>
          {hasAtLEastOneWeekDaySelected && (
            <StocksCalendarFormTimeAndPrice form={form} offer={offer} />
          )}
        </>
      )}
    </div>
  )
}
