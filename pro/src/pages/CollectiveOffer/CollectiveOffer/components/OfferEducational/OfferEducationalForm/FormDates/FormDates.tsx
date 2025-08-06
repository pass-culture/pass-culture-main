import { ChangeEvent } from 'react'
import { useFormContext } from 'react-hook-form'

import {
  OfferDatesType,
  OfferEducationalFormValues,
} from '@/commons/core/OfferEducational/types'
import { isDateValid } from '@/commons/utils/date'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { RadioButtonGroup } from '@/design-system/RadioButtonGroup/RadioButtonGroup'
import { Callout } from '@/ui-kit/Callout/Callout'
import { DatePicker } from '@/ui-kit/form/DatePicker/DatePicker'
import { TimePicker } from '@/ui-kit/form/TimePicker/TimePicker'

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
      <RadioButtonGroup
        disabled={disableForm}
        label="Quand votre offre peut-elle avoir lieu ?"
        labelTag="h2"
        checkedOption={watch('datesType')}
        variant="detailed"
        onChange={(e) => {
          setValue('datesType', e.target.value as OfferDatesType)
        }}
        options={[
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
        name="datesType"
        required
      />
    </div>
  )
}
