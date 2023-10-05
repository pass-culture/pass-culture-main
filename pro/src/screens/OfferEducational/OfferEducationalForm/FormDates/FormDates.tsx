import { useFormikContext } from 'formik'
import React from 'react'

import Callout from 'components/Callout/Callout'
import { CalloutVariant } from 'components/Callout/types'
import FormLayout from 'components/FormLayout'
import { OfferEducationalFormValues } from 'core/OfferEducational'
import { DatePicker, TimePicker } from 'ui-kit'
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
  const minBegginningDate = dateCreated ? new Date(dateCreated) : new Date()
  const minDateForEndingDate = isDateValid(values.begginningDate)
    ? new Date(values.begginningDate)
    : new Date()
  return (
    <FormLayout.Section
      title="Date et heure"
      description="Indiquez la date et l'heure ou la période pendant laquelle votre offre peut avoir lieu."
    >
      <Callout type={CalloutVariant.INFO} className={styles.banner}>
        Votre offre sera désactivée automatiquement à l'issue des dates
        précisées ci-dessous.
      </Callout>
      <FormLayout.Row className={styles.container}>
        <DatePicker
          name="begginningDate"
          label="Date de début"
          disabled={disableForm}
          minDate={minBegginningDate}
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
          label="Horraire"
          disabled={disableForm}
          isOptional
          hideFooter
        />
      </FormLayout.Row>
    </FormLayout.Section>
  )
}

export default FormDates
