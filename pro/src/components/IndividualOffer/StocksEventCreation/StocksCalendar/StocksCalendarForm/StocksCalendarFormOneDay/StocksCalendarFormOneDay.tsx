import { isValid } from 'date-fns'
import { UseFormReturn } from 'react-hook-form'

import { GetIndividualOfferWithAddressResponseModel } from 'apiClient/v1'
import {
  StocksCalendarFormValues,
  TimeSlotTypeOption,
} from 'components/IndividualOffer/StocksEventCreation/form/types'
import { RadioVariant } from 'ui-kit/form/shared/BaseRadio/BaseRadio'
import { DatePicker } from 'ui-kit/formV2/DatePicker/DatePicker'
import { RadioGroup } from 'ui-kit/formV2/RadioGroup/RadioGroup'

import { StocksCalendarFormSpecificTimeSlots } from '../StocksCalendarFormSpecificTimeSlots/StocksCalendarFormSpecificTimeSlots'
import { StocksCalendarLimitDates } from '../StocksCalendarLimitDates/StocksCalendarLimitDates'
import { StocksCalendarPriceCategories } from '../StocksCalendarPriceCategories/StocksCalendarPriceCategories'

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
        <>
          <RadioGroup
            name="timeSlotType"
            legend={
              <h2 className={styles['title']}>Le public doit se présenter :</h2>
            }
            variant={RadioVariant.BOX}
            className={styles['time-slot-type-group']}
            displayMode="inline-grow"
            checkedOption={form.watch('timeSlotType')}
            onChange={(e) =>
              form.setValue(
                'timeSlotType',
                e.target.value as TimeSlotTypeOption
              )
            }
            group={[
              {
                label: 'À un horaire précis',
                value: TimeSlotTypeOption.SPECIFIC_TIME,
                description:
                  'Le jeune doit réserver et se présenter sur un des horaires précis que vous avez défini.',
              },
              {
                label: 'Aux horaires d’ouverture',
                value: TimeSlotTypeOption.OPENING_HOURS,
                description:
                  'Le jeune se présente à n’importe quel moment sur les horaires d’ouverture que vous avez défini.',
              },
            ]}
          />
          <div className={styles['time-slots']}>
            {form.watch('timeSlotType') ===
              TimeSlotTypeOption.SPECIFIC_TIME && (
              <StocksCalendarFormSpecificTimeSlots form={form} />
            )}
          </div>

          <div className={styles['pricing-categories']}>
            <StocksCalendarPriceCategories
              form={form}
              priceCategories={offer.priceCategories}
            />
          </div>

          <div className={styles['limit-dates']}>
            <StocksCalendarLimitDates form={form} />
          </div>
        </>
      )}
    </div>
  )
}
