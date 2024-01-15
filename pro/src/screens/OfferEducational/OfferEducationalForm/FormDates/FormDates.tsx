import { useFormikContext } from 'formik'
import React from 'react'

import Callout from 'components/Callout/Callout'
import { CalloutVariant } from 'components/Callout/types'
import FormLayout from 'components/FormLayout'
import { OfferEducationalFormValues } from 'core/OfferEducational'
import { DatePicker, RadioGroup, TimePicker } from 'ui-kit'
import { BaseRadioVariant } from 'ui-kit/form/shared/BaseRadio/types'
import { isDateValid } from 'utils/date'

import styles from './FormDates.module.scss'
export interface FormDatesProps {
  disableForm: boolean
  dateCreated: string | undefined
}

const FormDates = ({
  disableForm,
  dateCreated,
}: FormDatesProps): JSX.Element => {
  const { values } = useFormikContext<OfferEducationalFormValues>()
  const minBeginningDate = dateCreated ? new Date(dateCreated) : new Date()
  const minDateForEndingDate = isDateValid(values.beginningDate)
    ? new Date(values.beginningDate)
    : new Date()
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
        variant={BaseRadioVariant.SECONDARY}
        withBorder
        legend="Quand votre offre peut-elle avoir lieu ?"
        name="datesType"
      />
      {values.datesType === 'specific_dates' && (
        <>
          <Callout type={CalloutVariant.INFO} className={styles.banner}>
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

export default FormDates
