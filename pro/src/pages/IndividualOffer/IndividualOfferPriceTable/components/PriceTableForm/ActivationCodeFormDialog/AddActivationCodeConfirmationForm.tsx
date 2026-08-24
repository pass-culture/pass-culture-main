import type React from 'react'

import { formatShortDateForInput, isDateValid } from '@/commons/utils/date'
import { getLocalDepartementDateTimeFromUtc } from '@/commons/utils/timezone'
import { Banner, BannerVariants } from '@/design-system/Banner/Banner'
import { DatePicker } from '@/ui-kit/form/DatePicker/DatePicker'

import styles from './ActivationCodeFormDialog.module.scss'

interface AddActivationCodeConfirmationFormProps {
  onExpirationDateChange: (expirationDate: string | undefined) => void
  today: Date
  minExpirationDate: Date | null
  departmentCode: string
}

export const AddActivationCodeConfirmationForm = ({
  onExpirationDateChange,
  today,
  minExpirationDate,
  departmentCode,
}: AddActivationCodeConfirmationFormProps) => {
  const getMinimumExpirationDatetime = (date: Date) => {
    const result = new Date(date)
    result.setDate(result.getDate() + 7)
    return result
  }
  const minDate = minExpirationDate ?? today

  return (
    <>
      <div className={styles['activation-codes-confirmation-intro']}>
        <p>
          Veuillez ajouter une date de fin de validité. Cette date ne doit pas
          être antérieure à la date limite de réservation.
        </p>
      </div>

      <div className={styles['activation-codes-form-dates']}>
        <DatePicker
          onChange={(event: React.ChangeEvent<HTMLInputElement>) => {
            if (!event.target.value || !isDateValid(event.target.value)) {
              onExpirationDateChange(undefined)
              return
            }

            const normalizedDate = formatShortDateForInput(
              getLocalDepartementDateTimeFromUtc(
                event.target.value,
                departmentCode
              )
            )
            onExpirationDateChange(normalizedDate)
          }}
          label={'Date de fin de validité'}
          name="activationCodesExpirationDatetime"
          minDate={getMinimumExpirationDatetime(minDate)}
          required
        />
      </div>
      <Banner
        variant={BannerVariants.WARNING}
        title="Cette opération est irréversible"
        description="Après l’ajout de vos codes, vous ne pourrez modifier ni la quantité ni la date de validité de ceux-ci."
      />
    </>
  )
}
