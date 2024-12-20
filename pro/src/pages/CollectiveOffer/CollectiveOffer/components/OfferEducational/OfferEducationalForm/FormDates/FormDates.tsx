import { useFormikContext } from 'formik'
import { ChangeEvent } from 'react'

import { OfferEducationalFormValues } from 'commons/core/OfferEducational/types'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { isDateValid } from 'commons/utils/date'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { Callout } from 'ui-kit/Callout/Callout'
import { CalloutVariant } from 'ui-kit/Callout/types'
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
  const areNewStatusesEnabled = useActiveFeature(
    'ENABLE_COLLECTIVE_NEW_STATUSES'
  )
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

  const deactivateWording = areNewStatusesEnabled
    ? 'mise en pause'
    : 'désactivée'

  return (
    <FormLayout.Section title="Date et heure">
      <RadioGroup
        disabled={disableForm}
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
        variant={RadioVariant.BOX}
        legend="Quand votre offre peut-elle avoir lieu ?"
        name="datesType"
      />
      {values.datesType === 'specific_dates' && (
        <>
          <Callout variant={CalloutVariant.INFO} className={styles.banner}>
            {`Votre offre sera ${deactivateWording} automatiquement à l’issue des dates
            précisées ci-dessous.`}
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
