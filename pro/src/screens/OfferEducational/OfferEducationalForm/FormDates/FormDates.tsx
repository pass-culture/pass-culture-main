import { useFormikContext } from 'formik'
import { ChangeEvent } from 'react'

import Callout from 'components/Callout/Callout'
import { CalloutVariant } from 'components/Callout/types'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { OfferEducationalFormValues } from 'core/OfferEducational/types'
import { DatePicker } from 'ui-kit/form/DatePicker/DatePicker'
import { RadioGroup } from 'ui-kit/form/RadioGroup/RadioGroup'
import { TimePicker } from 'ui-kit/form/TimePicker/TimePicker'
import { isDateValid } from 'utils/date'

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
    <FormLayout.Section title="Date et heure">
      <RadioGroup
        group={[
          {
            label: 'Tout au long de l’année scolaire, l’offre est permanente',
            value: 'permanent',
          },
          {
            label: 'Pendant une période précise uniquement',
            value: 'specific_dates',
          },
        ]}
        withBorder
        legend="Quand votre offre peut-elle avoir lieu ?"
        name="datesType"
      />
      {values.datesType === 'specific_dates' && (
        <>
          <Callout variant={CalloutVariant.INFO} className={styles.banner}>
            Votre offre sera désactivée automatiquement à l’issue des dates
            précisées ci-dessous.
          </Callout>
          <FormLayout.Row className={styles.container}>
            <DatePicker
              name="beginningDate"
              label="Date de début"
              disabled={disableForm}
              minDate={minBeginningDate}
              hideFooter
              onChange={handleBeginningDateChange}
            />
            <DatePicker
              name="endingDate"
              label="Date de fin"
              disabled={disableForm}
              minDate={minDateForEndingDate}
              hideFooter
            />
            <TimePicker
              name="hour"
              label="Horaire"
              disabled={disableForm}
              isOptional
              hideFooter
            />
          </FormLayout.Row>
        </>
      )}
    </FormLayout.Section>
  )
}
