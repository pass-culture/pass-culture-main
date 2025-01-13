import { useFormikContext } from 'formik'

import { SelectOption } from 'commons/custom_types/form'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { Divider } from 'ui-kit/Divider/Divider'
import { DatePicker } from 'ui-kit/form/DatePicker/DatePicker'
import { RadioButton } from 'ui-kit/form/RadioButton/RadioButton'
import { Select } from 'ui-kit/form/Select/Select'
import { RadioVariant } from 'ui-kit/form/shared/BaseRadio/BaseRadio'
import { InfoBox } from 'ui-kit/InfoBox/InfoBox'

import styles from './EventPublicationForm.module.scss'
import { EventPublicationFormValues } from './types'

const hours = [
  '00',
  '01',
  '02',
  '03',
  '04',
  '05',
  '06',
  '07',
  '08',
  '09',
  '10',
  '11',
  '12',
  '13',
  '14',
  '15',
  '16',
  '17',
  '18',
  '19',
  '20',
  '21',
  '22',
  '23',
]

const minutes = ['00', '15', '30', '45']

const getPublicationHoursOptions = (): SelectOption[] => {
  const options = []

  for (const hour of hours) {
    for (const minute of minutes) {
      const option = `${hour}:${minute}`
      options.push({ label: option, value: option })
    }
  }

  return options
}

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
                variant={RadioVariant.BOX}
              />

              <RadioButton
                label="À une date et heure précise"
                name="publicationMode"
                value="later"
                variant={RadioVariant.BOX}
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
                options={getPublicationHoursOptions()}
              />
            </FormLayout.Row>
          )}
        </FormLayout.Section>
      </FormLayout>

      <Divider />
    </>
  )
}
