import { UseFormReturn } from 'react-hook-form'

import { GetIndividualOfferWithAddressResponseModel } from 'apiClient/v1'
import { useIndividualOfferContext } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import {
  DurationTypeOption,
  StocksCalendarFormValues,
  TimeSlotTypeOption,
} from 'components/IndividualOffer/StocksEventCreation/form/types'
import { Callout } from 'ui-kit/Callout/Callout'
import { CalloutVariant } from 'ui-kit/Callout/types'
import { RadioGroup } from 'ui-kit/formV2/RadioGroup/RadioGroup'

import { StocksCalendarFormSpecificTimeSlots } from './StocksCalendarFormSpecificTimeSlots/StocksCalendarFormSpecificTimeSlots'
import styles from './StocksCalendarFormTimeAndPrice.module.scss'
import { StocksCalendarLimitDates } from './StocksCalendarLimitDates/StocksCalendarLimitDates'
import { StocksCalendarPriceCategories } from './StocksCalendarPriceCategories/StocksCalendarPriceCategories'

export function StocksCalendarFormTimeAndPrice({
  form,
  offer,
}: {
  form: UseFormReturn<StocksCalendarFormValues>
  offer: GetIndividualOfferWithAddressResponseModel
}) {
  const multipleDaysNoEndDateSpecificTime =
    form.watch('durationType') === DurationTypeOption.MULTIPLE_DAYS_WEEKS &&
    form.watch('timeSlotType') === TimeSlotTypeOption.SPECIFIC_TIME &&
    form.watch('multipleDaysHasNoEndDate')

  const { subCategories } = useIndividualOfferContext()

  const isOfferEligibleToOpeningHours = subCategories.find(
    (cat) => cat.id === offer.subcategoryId
  )?.canHaveOpeningHours

  if (!isOfferEligibleToOpeningHours) {
    return (
      <>
        <div className={styles['time-slots']}>
          <StocksCalendarFormSpecificTimeSlots form={form} />
        </div>
        <StocksCalendarFormPriceCategoryAndLimitDates
          form={form}
          offer={offer}
        />
      </>
    )
  }
  const cannotAddOpeningHoursBecauseOfferHasStocks =
    offer.hasStocks &&
    form.watch('timeSlotType') === TimeSlotTypeOption.OPENING_HOURS

  const showErrorCallout =
    multipleDaysNoEndDateSpecificTime ||
    cannotAddOpeningHoursBecauseOfferHasStocks

  return (
    <>
      <RadioGroup
        name="timeSlotType"
        legend={
          <h2 className={styles['title']}>Le public doit se présenter :</h2>
        }
        variant="detailed"
        className={styles['time-slot-type-group']}
        displayMode="inline-grow"
        checkedOption={form.watch('timeSlotType')}
        onChange={(e) =>
          form.setValue('timeSlotType', e.target.value as TimeSlotTypeOption)
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
      {showErrorCallout ? (
        <Callout
          variant={CalloutVariant.ERROR}
          className={styles['error-callout']}
        >
          {cannotAddOpeningHoursBecauseOfferHasStocks
            ? 'Pour ajouter des horaires d’ouverture, vous devez supprimer toutes les dates que vous avez déjà ajoutées.'
            : 'En n’indiquant pas de date de fin, vous ne pouvez pas choisir l’option horaires précis.'}
        </Callout>
      ) : (
        <>
          <div className={styles['time-slots']}>
            {form.watch('timeSlotType') ===
              TimeSlotTypeOption.SPECIFIC_TIME && (
              <StocksCalendarFormSpecificTimeSlots form={form} />
            )}
          </div>

          <StocksCalendarFormPriceCategoryAndLimitDates
            form={form}
            offer={offer}
          />
        </>
      )}
    </>
  )
}

function StocksCalendarFormPriceCategoryAndLimitDates({
  form,
  offer,
}: {
  form: UseFormReturn<StocksCalendarFormValues>
  offer: GetIndividualOfferWithAddressResponseModel
}) {
  return (
    <>
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
  )
}
