import { ChangeEvent, useId } from 'react'
import { useFormContext } from 'react-hook-form'

import {
  OfferDatesType,
  OfferEducationalFormValues,
} from 'commons/core/OfferEducational/types'
import { isDateValid } from 'commons/utils/date'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { Callout } from 'ui-kit/Callout/Callout'
import { DatePicker } from 'ui-kit/form/DatePicker/DatePicker'
import { RadioGroup } from 'ui-kit/form/RadioGroup/RadioGroup'
import { TimePicker } from 'ui-kit/form/TimePicker/TimePicker'

import styles from './FormDates.module.scss'

export interface FormDatesProps {
  disableForm: boolean
  dateCreated: string | undefined
}

export const FormDates = ({
  disableForm,
  dateCreated,
}: FormDatesProps): JSX.Element => {
  const { watch, setValue, register, getFieldState } =
    useFormContext<OfferEducationalFormValues>()

  const beginningDateValue = watch('beginningDate')

  const subtitleId = useId()

  const minBeginningDate = dateCreated ? new Date(dateCreated) : new Date()
  const minDateForEndingDate = isDateValid(beginningDateValue)
    ? new Date(beginningDateValue)
    : new Date()

  function handleBeginningDateChange(e: ChangeEvent<HTMLInputElement>) {
    const newBeginningDate = e.target.value

    setValue('beginningDate', newBeginningDate)

    if (newBeginningDate) {
      setValue('endingDate', newBeginningDate)
    }
  }

  return (
    <div className={styles['container']}>
      <h2 id={subtitleId} className={styles['subtitle']}>
        Quand votre offre peut-elle avoir lieu ? *
      </h2>
      <RadioGroup
        disabled={disableForm}
        checkedOption={watch('datesType')}
        variant="detailed"
        onChange={(e) => {
          setValue('datesType', e.target.value as OfferDatesType)
        }}
        group={[
          {
            label: 'Tout au long de l’année scolaire, l’offre est permanente',
            value: 'permanent',
          },
          {
            label: 'À une date ou une période précise',
            value: 'specific_dates',
            collapsed: (
              <>
                <Callout className={styles.banner}>
                  Votre offre sera mise en pause automatiquement à l’issue des
                  dates précisées ci-dessous.
                </Callout>
                <FormLayout.Row className={styles['row-container']}>
                  <DatePicker
                    label="Date de début"
                    {...register('beginningDate')}
                    error={getFieldState('beginningDate').error?.message}
                    disabled={disableForm}
                    minDate={minBeginningDate}
                    onChange={handleBeginningDateChange}
                    required
                  />
                  <DatePicker
                    {...register('endingDate')}
                    error={getFieldState('endingDate').error?.message}
                    label="Date de fin"
                    disabled={disableForm}
                    minDate={minDateForEndingDate}
                    required
                  />
                  <TimePicker
                    {...register('hour')}
                    error={getFieldState('hour').error?.message}
                    label="Horaire"
                    disabled={disableForm}
                  />
                </FormLayout.Row>
              </>
            ),
          },
        ]}
        describedBy={subtitleId}
        name="datesType"
      />
    </div>
  )
}
