import { useFormikContext } from 'formik'

import { SelectOption } from 'commons/custom_types/form'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { Divider } from 'ui-kit/Divider/Divider'
import { DatePicker } from 'ui-kit/form/DatePicker/DatePicker'
import { Select } from 'ui-kit/form/Select/Select'
import { RadioGroup } from 'ui-kit/formV2/RadioGroup/RadioGroup'
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
  const { values, handleChange } =
    useFormikContext<EventPublicationFormValues>()

  const PublicationDatePicker = values.publicationMode === 'later' && (
    <FormLayout.Row inline className={styles['publish-later']}>
      <DatePicker
        label="Date"
        name="publicationDate"
        minDate={today}
        className={styles['date-picker']}
      />
      <Select
        label="Heure"
        name="publicationTime"
        options={getPublicationHoursOptions()}
        defaultOption={{ label: 'HH:MM', value: '' }}
        className={styles['time-picker']}
      />
    </FormLayout.Row>
  )

  return (
    <>
      <FormLayout fullWidthActions className={styles['form']}>
        <FormLayout.Section title="Date de publication">
          <FormLayout.Row
            sideComponent={
              <InfoBox>
                Dans le cas où votre offre est en instruction par l’équipe
                Conformité, sa validation peut prendre jusqu’à 72h. <br />
                Après validation elle sera automatiquement publiée ou programmée
                comme vous l’avez choisi.
              </InfoBox>
            }
          >
            <RadioGroup
              legend="Quand votre offre doit-elle être publiée dans l’application ?"
              name="publicationMode"
              variant="detailed"
              group={[
                { label: 'Publier maintenant', value: 'now', sizing: 'fill' },
                {
                  label: 'Publier plus tard',
                  description:
                    'L’offre restera secrète pour le public jusqu’à sa publication.',
                  value: 'later',
                  sizing: 'fill',
                  collapsed: PublicationDatePicker,
                },
              ]}
              checkedOption={values.publicationMode}
              onChange={handleChange}
            />
          </FormLayout.Row>
        </FormLayout.Section>
      </FormLayout>

      <Divider />
    </>
  )
}
