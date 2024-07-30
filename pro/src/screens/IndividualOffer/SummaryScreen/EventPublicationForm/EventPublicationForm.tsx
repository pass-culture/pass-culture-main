import { useFormikContext } from 'formik'

import { FormLayout } from 'components/FormLayout/FormLayout'
import { SelectOption } from 'custom_types/form'
import { Divider } from 'ui-kit/Divider/Divider'
import { DatePicker } from 'ui-kit/form/DatePicker/DatePicker'
import { RadioButton } from 'ui-kit/form/RadioButton/RadioButton'
import { Select } from 'ui-kit/form/Select/Select'
import { InfoBox } from 'ui-kit/InfoBox/InfoBox'

import styles from './EventPublicationForm.module.scss'
import { EventPublicationFormValues } from './types'

const publicationHoursOptions: SelectOption[] = [
  { label: '00:00', value: '00:00' },
  { label: '01:00', value: '01:00' },
  { label: '02:00', value: '02:00' },
  { label: '03:00', value: '03:00' },
  { label: '04:00', value: '04:00' },
  { label: '05:00', value: '05:00' },
  { label: '06:00', value: '06:00' },
  { label: '07:00', value: '07:00' },
  { label: '08:00', value: '08:00' },
  { label: '09:00', value: '09:00' },
  { label: '10:00', value: '10:00' },
  { label: '11:00', value: '11:00' },
  { label: '12:00', value: '12:00' },
  { label: '13:00', value: '13:00' },
  { label: '14:00', value: '14:00' },
  { label: '15:00', value: '15:00' },
  { label: '16:00', value: '16:00' },
  { label: '17:00', value: '17:00' },
  { label: '18:00', value: '18:00' },
  { label: '19:00', value: '19:00' },
  { label: '20:00', value: '20:00' },
  { label: '21:00', value: '21:00' },
  { label: '22:00', value: '22:00' },
  { label: '23:00', value: '23:00' },
]

export const EventPublicationForm = () => {
  const today = new Date()
  const { values } = useFormikContext<EventPublicationFormValues>()

  return (
    <>
      <FormLayout fullWidthActions className={styles['form']}>
        <FormLayout.Section title="Date de publication">
          <FormLayout.Row
            sideComponent={
              values.publicationMode === 'later' ? (
                <InfoBox>
                  Votre offre doit être validée, ce qui peut prendre jusqu’à
                  72h. Après validation elle sera automatiquement publiée à la
                  date et heure indiquées.
                </InfoBox>
              ) : null
            }
          >
            <div className={styles['radio-group']}>
              <RadioButton
                label="Tout de suite"
                name="publicationMode"
                value="now"
                withBorder
              />

              <RadioButton
                label="À une date et heure précise"
                name="publicationMode"
                value="later"
                withBorder
              />
            </div>
          </FormLayout.Row>

          {values.publicationMode === 'later' && (
            <FormLayout.Row inline>
              <DatePicker
                label="Date de publication"
                name="publicationDate"
                minDate={today}
              />

              <Select
                label="Heure de publication"
                name="publicationTime"
                options={publicationHoursOptions}
              />
            </FormLayout.Row>
          )}
        </FormLayout.Section>
      </FormLayout>

      <Divider />
    </>
  )
}
