import { useFormContext } from 'react-hook-form'

import { RadioButtonGroup } from '@/design-system/RadioButtonGroup/RadioButtonGroup'
import { DateAndTimePicker } from '@/ui-kit/form/DateAndTimePicker/DateAndTimePicker'

import styles from './PublicationAndBookingFields.module.css'

type PublicationAndBookingFieldsProps = {
  disabled?: boolean
  maxDate?: string
}

export const PublicationAndBookingFields = ({
  disabled = false,
  maxDate,
}: PublicationAndBookingFieldsProps) => {
  const { watch, setValue } = useFormContext()

  const publicationMode = watch('publicationMode')
  const bookingAllowedMode = watch('bookingAllowedMode')

  return (
    <>
      <div className={styles['group']}>
        <RadioButtonGroup
          label="Quand votre offre doit-elle être publiée&nbsp;?"
          name="publicationMode"
          variant="detailed"
          disabled={disabled}
          checkedOption={disabled ? undefined : publicationMode}
          onChange={(e) => setValue('publicationMode', e.target.value)}
          options={[
            { label: 'Publier maintenant', value: 'now' },
            {
              label: 'Publier plus tard',
              description:
                'L’offre restera secrète pour le public jusqu’à sa publication.',
              value: 'later',
              collapsed: publicationMode === 'later' && (
                <DateAndTimePicker
                  dateName="publicationDate"
                  timeName="publicationTime"
                  disabled={disabled}
                  maxDate={maxDate ? new Date(maxDate) : undefined}
                />
              ),
            },
          ]}
        />
      </div>
      <div className={styles['group']}>
        <RadioButtonGroup
          label="Quand votre offre pourra-t-elle être réservable&nbsp;?"
          name="bookingAllowedMode"
          variant="detailed"
          disabled={disabled}
          checkedOption={disabled ? undefined : bookingAllowedMode}
          onChange={(e) => setValue('bookingAllowedMode', e.target.value)}
          options={[
            {
              label: 'Rendre réservable dès la publication',
              value: 'now',
            },
            {
              label: 'Rendre réservable plus tard',
              description:
                'En activant cette option, vous permettez au public de visualiser l’entièreté de votre offre, de la mettre en favori et pouvoir la suivre mais sans qu’elle puisse être réservable.',
              value: 'later',
              collapsed: bookingAllowedMode === 'later' && (
                <DateAndTimePicker
                  dateName="bookingAllowedDate"
                  timeName="bookingAllowedTime"
                  disabled={disabled}
                  maxDate={maxDate ? new Date(maxDate) : undefined}
                />
              ),
            },
          ]}
        />
      </div>
    </>
  )
}
