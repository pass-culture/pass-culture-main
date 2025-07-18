import { type ChangeEvent } from 'react'
import { useFormContext } from 'react-hook-form'

import { SelectOption } from 'commons/custom_types/form'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { Tag, TagVariant } from 'design-system/Tag/Tag'
import { Divider } from 'ui-kit/Divider/Divider'
import { DatePicker } from 'ui-kit/form/DatePicker/DatePicker'
import { RadioGroup } from 'ui-kit/form/RadioGroup/RadioGroup'
import { Select } from 'ui-kit/form/Select/Select'
import { TipsBanner } from 'ui-kit/TipsBanner/TipsBanner'

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

export const getPublicationHoursOptions = (): SelectOption[] => {
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

  const { register, watch, setValue, formState, trigger } =
    useFormContext<EventPublicationFormValues>()
  const publicationMode = watch('publicationMode')

  const isNewPublicationDatetimeEnabled = useActiveFeature(
    'WIP_REFACTO_FUTURE_OFFER'
  )

  const sectionTitle = isNewPublicationDatetimeEnabled ? (
    <div className={styles['title-container']}>
      <span className={styles['title']}>Publication et réservation</span>
      <div className={styles['tag']}>
        <Tag label="Nouveau" variant={TagVariant.NEW} />
      </div>
    </div>
  ) : (
    'Date de publication'
  )

  const updatePublicationDate = (event: ChangeEvent<HTMLInputElement>) => {
    const nextPublicationDate = event.target.value

    setValue('publicationDate', nextPublicationDate, { shouldValidate: true })
  }

  const updatePublicationTime = async (
    event: ChangeEvent<HTMLSelectElement>
  ) => {
    const nextPublicationTime = event.target.value

    setValue('publicationTime', nextPublicationTime)

    await trigger('publicationDate')
  }

  return (
    <>
      <FormLayout fullWidthActions className={styles['form']}>
        <FormLayout.Section title={sectionTitle}>
          <FormLayout.MandatoryInfo />
          <FormLayout.Row
            sideComponent={
              <TipsBanner>
                Dans le cas où votre offre est en instruction par l’équipe
                Conformité, sa validation peut prendre jusqu’à 72h. <br />
                Après validation elle sera automatiquement publiée ou programmée
                comme vous l’avez choisi.
              </TipsBanner>
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
                  collapsed: publicationMode === 'later' && (
                    <FormLayout.Row inline className={styles['publish-later']}>
                      <DatePicker
                        label="Date"
                        minDate={today}
                        className={styles['date-picker']}
                        required
                        {...register('publicationDate', {
                          onChange: updatePublicationDate,
                        })}
                        error={formState.errors.publicationDate?.message}
                      />
                      <Select
                        label="Heure"
                        options={getPublicationHoursOptions()}
                        defaultOption={{ label: 'HH:MM', value: '' }}
                        className={styles['time-picker']}
                        required
                        {...register('publicationTime', {
                          onChange: updatePublicationTime,
                        })}
                        error={formState.errors.publicationTime?.message}
                      />
                    </FormLayout.Row>
                  ),
                },
              ]}
              checkedOption={watch('publicationMode')}
              onChange={(event) => {
                setValue(
                  'publicationMode',
                  event.target
                    .value as EventPublicationFormValues['publicationMode']
                )
              }}
            />
          </FormLayout.Row>
        </FormLayout.Section>
        {isNewPublicationDatetimeEnabled && (
          <FormLayout.Section>
            <RadioGroup
              legend="Quand votre offre pourra être réservable ?"
              name="bookingAllowedMode"
              variant="detailed"
              group={[
                {
                  label: 'Rendre réservable dès la publication',
                  value: 'now',
                  sizing: 'fill',
                },
                {
                  label: 'Rendre réservable plus tard',
                  description:
                    'En activant cette option, vous permettez au public de visualiser l’entièreté de votre offre, de la mettre en favori et pouvoir la suivre mais sans qu’elle puisse être réservable.',
                  value: 'later',
                  sizing: 'fill',
                  collapsed: watch('bookingAllowedMode') === 'later' && (
                    <FormLayout.Row inline className={styles['publish-later']}>
                      <DatePicker
                        label="Date"
                        minDate={today}
                        className={styles['date-picker']}
                        required
                        {...register('bookingAllowedDate')}
                        error={formState.errors.bookingAllowedDate?.message}
                      />
                      <Select
                        label="Heure"
                        options={getPublicationHoursOptions()}
                        defaultOption={{ label: 'HH:MM', value: '' }}
                        className={styles['time-picker']}
                        required
                        {...register('bookingAllowedTime')}
                        error={formState.errors.bookingAllowedTime?.message}
                      />
                    </FormLayout.Row>
                  ),
                },
              ]}
              checkedOption={watch('bookingAllowedMode')}
              onChange={(event) => {
                setValue(
                  'bookingAllowedMode',
                  event.target
                    .value as EventPublicationFormValues['bookingAllowedMode']
                )
              }}
            />
          </FormLayout.Section>
        )}
      </FormLayout>

      <Divider />
    </>
  )
}
