import { useFormikContext } from 'formik'
import { ChangeEvent, useId } from 'react'

import { OfferEducationalFormValues } from 'commons/core/OfferEducational/types'
import { isDateValid } from 'commons/utils/date'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { Callout } from 'ui-kit/Callout/Callout'
import { DatePicker } from 'ui-kit/form/DatePicker/DatePicker'
import { RadioGroup } from 'ui-kit/form/RadioGroup/RadioGroup'
import { RadioVariant } from 'ui-kit/form/shared/BaseRadio/BaseRadio'
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
  const { values, setFieldValue } =
    useFormikContext<OfferEducationalFormValues>()

  const subtitleId = useId()

  const minBeginningDate = dateCreated ? new Date(dateCreated) : new Date()
  const minDateForEndingDate = isDateValid(values.beginningDate)
    ? new Date(values.beginningDate)
    : new Date()

  async function handleBeginningDateChange(e: ChangeEvent<HTMLInputElement>) {
    const newBeginningDate = e.target.value
    if (newBeginningDate) {
      await setFieldValue('endingDate', newBeginningDate)
    }
  }

  return (
    <div className={styles['container']}>
      <h2 id={subtitleId} className={styles['subtitle']}>
        Quand votre offre peut-elle avoir lieu ? *
      </h2>
      <RadioGroup
        disabled={disableForm}
        group={[
          {
            label: 'Tout au long de l’année scolaire, l’offre est permanente',
            value: 'permanent',
          },
          {
            label: 'À une date ou une période précise',
            value: 'specific_dates',
            childrenOnChecked: (
              <>
                <Callout className={styles.banner}>
                  Votre offre sera mise en pause automatiquement à l’issue des
                  dates précisées ci-dessous.
                </Callout>
                <FormLayout.Row className={styles['row-container']}>
                  <DatePicker
                    name="beginningDate"
                    label="Date de début"
                    disabled={disableForm}
                    minDate={minBeginningDate}
                    onChange={handleBeginningDateChange}
                  />
                  <DatePicker
                    name="endingDate"
                    label="Date de fin"
                    disabled={disableForm}
                    minDate={minDateForEndingDate}
                  />
                  <TimePicker
                    name="hour"
                    label="Horaire"
                    disabled={disableForm}
                    isOptional
                  />
                </FormLayout.Row>
              </>
            ),
          },
        ]}
        variant={RadioVariant.BOX}
        describedBy={subtitleId}
        name="datesType"
      />
    </div>
  )
}
