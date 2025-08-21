import { useId } from 'react'
import { useFormContext } from 'react-hook-form'

import type { GetIndividualOfferWithAddressResponseModel } from '@/apiClient/v1'
import type { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import { MandatoryInfo } from '@/components/FormLayout/FormLayoutMandatoryInfo'
import { getPriceCategoryOptions } from '@/components/IndividualOffer/PriceCategoriesScreen/form/getPriceCategoryOptions'
import { OpeningHours } from '@/components/OpeningHours/OpeningHours'
import { ScrollToFirstHookFormErrorAfterSubmit } from '@/components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { Checkbox } from '@/design-system/Checkbox/Checkbox'
import { DatePicker } from '@/ui-kit/form/DatePicker/DatePicker'
import { FieldError } from '@/ui-kit/form/shared/FieldError/FieldError'

import type { IndividualOfferTimetableFormValues } from '../../commons/types'
import { QuantityPerPriceCategory } from '../QuantityPerPriceCategory/QuantityPerPriceCategory'
import styles from './TimetableOpeningHours.module.scss'
import { TimetableOpeningHoursActionsBar } from './TimetableOpeningHoursActionsBar/TimetableOpeningHoursActionsBar'

type TimetableOpeningHoursProps = {
  offer: GetIndividualOfferWithAddressResponseModel
  mode: OFFER_WIZARD_MODE
  timetableTypeRadioGroupShown: boolean
}

export function TimetableOpeningHours({
  offer,
  mode,
  timetableTypeRadioGroupShown,
}: TimetableOpeningHoursProps) {
  const form = useFormContext<IndividualOfferTimetableFormValues>()

  const openingHoursErrorId = useId()

  const openingHoursError =
    form.formState.errors.openingHours?.root?.message ||
    form.formState.errors.openingHours?.message

  const priceCategoryOptions = getPriceCategoryOptions(offer.priceCategories)

  return (
    <>
      <MandatoryInfo />
      <ScrollToFirstHookFormErrorAfterSubmit />
      <div className={styles['dates']}>
        <DatePicker
          label="Date de début"
          {...form.register('startDate')}
          error={form.formState.errors.startDate?.message}
          required
        />
        {!form.watch('noEndDate') && (
          <DatePicker
            label="Date de fin"
            {...form.register('endDate')}
            error={form.formState.errors.endDate?.message}
            required
          />
        )}
        <div className={styles['dates-checkbox']}>
          <Checkbox
            label="Pas de date de fin"
            name="noEndDate"
            checked={form.watch('noEndDate')}
            onChange={(e) => form.setValue('noEndDate', e.target.checked)}
          />
        </div>
      </div>
      <fieldset
        className={styles['openging-hours']}
        aria-describedby={openingHoursErrorId}
      >
        <legend>
          {timetableTypeRadioGroupShown ? (
            <h3 className={styles['title']}>Horaires d’accès</h3>
          ) : (
            <h2 className={styles['title']}>Horaires d’accès</h2>
          )}
        </legend>
        <OpeningHours
          hasErrorBecauseOfEmptyOpeningHours={Boolean(openingHoursError)}
        />
        <div id={openingHoursErrorId} role="alert">
          {openingHoursError && <FieldError>{openingHoursError}</FieldError>}
        </div>
      </fieldset>
      <fieldset className={styles['price-categories']}>
        <legend>
          {timetableTypeRadioGroupShown ? (
            <h3 className={styles['title']}>Places et tarifs</h3>
          ) : (
            <h3 className={styles['title']}>Places et tarifs</h3>
          )}
        </legend>
        <QuantityPerPriceCategory priceCategoryOptions={priceCategoryOptions} />
      </fieldset>
      <TimetableOpeningHoursActionsBar offer={offer} mode={mode} />
    </>
  )
}
