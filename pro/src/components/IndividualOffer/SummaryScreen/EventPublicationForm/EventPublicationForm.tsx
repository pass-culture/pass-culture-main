import { useFormContext } from 'react-hook-form'

import { SelectOption } from 'commons/custom_types/form'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { Divider } from 'ui-kit/Divider/Divider'
import { RadioVariant } from 'ui-kit/form/shared/BaseRadio/BaseRadio'
import { DatePicker } from 'ui-kit/formV2/DatePicker/DatePicker'
import { RadioButton } from 'ui-kit/formV2/RadioButton/RadioButton'
import { Select } from 'ui-kit/formV2/Select/Select'
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
  const {
    formState: { errors },
    register,
    watch,
    setValue,
  } = useFormContext<EventPublicationFormValues>()

  return (
    <>
      <FormLayout fullWidthActions className={styles['form']}>
        <FormLayout.Section title="Date de publication">
          <FormLayout.Row
            sideComponent={
              watch('publicationMode') === 'later' ? (
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
                {...register('publicationMode')}
                value="now"
                variant={RadioVariant.BOX}
                onChange={() => setValue('publicationMode', 'now')}
              />
              <RadioButton
                label="À une date et heure précise"
                {...register('publicationMode')}
                value="later"
                variant={RadioVariant.BOX}
                onChange={() => setValue('publicationMode', 'later')}
              />
            </div>
          </FormLayout.Row>

          {watch('publicationMode') === 'later' && (
            <FormLayout.Row inline>
              <DatePicker
                label="Date de publication"
                {...register('publicationDate')}
                required
                minDate={new Date()}
                error={errors.publicationDate?.message}
              />

              <Select
                label="Heure de publication"
                {...register('publicationTime')}
                options={getPublicationHoursOptions()}
                required
                defaultOption={{ label: 'HH:MM', value: '' }}
                error={errors.publicationTime?.message}
              />
            </FormLayout.Row>
          )}
        </FormLayout.Section>
      </FormLayout>

      <Divider />
    </>
  )
}
