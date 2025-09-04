import { useId } from 'react'
import { useFormContext } from 'react-hook-form'

import type { GetIndividualOfferWithAddressResponseModel } from '@/apiClient/v1'
import type { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import { MandatoryInfo } from '@/components/FormLayout/FormLayoutMandatoryInfo'
import { OpeningHours } from '@/components/OpeningHours/OpeningHours'
import { ScrollToFirstHookFormErrorAfterSubmit } from '@/components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { RadioButtonGroup } from '@/design-system/RadioButtonGroup/RadioButtonGroup'
import { getPriceCategoryOptions } from '@/pages/IndividualOffer/commons/getPriceCategoryOptions'
import { DatePicker } from '@/ui-kit/form/DatePicker/DatePicker'
import { FieldError } from '@/ui-kit/form/shared/FieldError/FieldError'

import {
  HasDateEnum,
  type IndividualOfferTimetableFormValues,
} from '../../commons/types'
import { QuantityPerPriceCategory } from '../QuantityPerPriceCategory/QuantityPerPriceCategory'
import styles from './TimetableOpeningHours.module.scss'
import { TimetableOpeningHoursActionsBar } from './TimetableOpeningHoursActionsBar/TimetableOpeningHoursActionsBar'

export type TimetableOpeningHoursProps = {
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
        <RadioButtonGroup
          variant="detailed"
          sizing="hug"
          display="horizontal"
          checkedOption={form.watch('hasStartDate')}
          onChange={(e) =>
            form.setValue(
              'hasStartDate',
              (e.target as HTMLInputElement)
                .value as IndividualOfferTimetableFormValues['hasStartDate']
            )
          }
          label="Peut-on en profiter dès aujourd’hui&nbsp;?"
          name="hasStartDate"
          options={[
            { label: 'Oui', value: HasDateEnum.YES },
            { label: 'Non', value: HasDateEnum.NO },
          ]}
        />
        {form.watch('hasStartDate') === HasDateEnum.YES && (
          <DatePicker
            className={styles['dates-input']}
            label="Date de début"
            {...form.register('startDate')}
            required
            error={form.formState.errors.startDate?.message}
          />
        )}
      </div>
      <div className={styles['dates']}>
        <RadioButtonGroup
          variant="detailed"
          sizing="hug"
          display="horizontal"
          label="Y a t-il une date limite de fin pour en profiter&nbsp;?"
          name="hasEndDate"
          checkedOption={form.watch('hasEndDate')}
          onChange={(e) =>
            form.setValue(
              'hasEndDate',
              (e.target as HTMLInputElement)
                .value as IndividualOfferTimetableFormValues['hasEndDate']
            )
          }
          options={[
            { label: 'Oui', value: HasDateEnum.YES },
            { label: 'Non', value: HasDateEnum.NO },
          ]}
        />
        {form.watch('hasEndDate') === HasDateEnum.YES && (
          <DatePicker
            className={styles['dates-input']}
            label="Date de fin"
            {...form.register('endDate')}
            required
            error={form.formState.errors.endDate?.message}
          />
        )}
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
          {openingHoursError && (
            <FieldError className={styles['error']}>
              {openingHoursError}
            </FieldError>
          )}
        </div>
      </fieldset>
      <fieldset className={styles['price-categories']}>
        <legend>
          {timetableTypeRadioGroupShown ? (
            <h3 className={styles['title']}>Places et tarifs</h3>
          ) : (
            <h2 className={styles['title']}>Places et tarifs</h2>
          )}
        </legend>
        <QuantityPerPriceCategory priceCategoryOptions={priceCategoryOptions} />
      </fieldset>
      <TimetableOpeningHoursActionsBar offer={offer} mode={mode} />
    </>
  )
}
