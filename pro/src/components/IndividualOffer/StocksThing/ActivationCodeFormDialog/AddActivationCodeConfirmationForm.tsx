import { ChangeEvent, useState } from 'react'

import { formatShortDateForInput, isDateValid } from 'commons/utils/date'
import { getLocalDepartementDateTimeFromUtc } from 'commons/utils/timezone'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { DatePicker } from 'ui-kit/form/DatePicker/DatePicker'

import styles from './ActivationCodeFormDialog.module.scss'

interface AddActivationCodeConfirmationFormProps {
  unsavedActivationCodes: string[] | undefined
  clearActivationCodes: () => void
  submitActivationCodes: (expirationDate: string | undefined) => void
  today: Date
  minExpirationDate: Date | null
  departmentCode: string
}

export const AddActivationCodeConfirmationForm = ({
  unsavedActivationCodes,
  clearActivationCodes,
  submitActivationCodes,
  today,
  minExpirationDate,
  departmentCode,
}: AddActivationCodeConfirmationFormProps) => {
  const [expirationDate, setExpirationDate] = useState<string | undefined>(
    undefined
  )
  const getMinimumExpirationDatetime = (date: Date) => {
    const result = new Date(date)
    result.setDate(result.getDate() + 7)
    return result
  }
  const minDate = minExpirationDate === null ? today : minExpirationDate

  return (
    <div className={styles['activation-codes-form']}>
      <div>
        <p>
          Vous êtes sur le point d’ajouter {unsavedActivationCodes?.length}{' '}
          codes d’activation.
        </p>
        <p>
          La quantité disponible pour cette offre sera mise à jour dans vos
          stocks.
        </p>
        <p>
          Veuillez ajouter une date de fin de validité. Cette date ne doit pas
          être antérieure à la date limite de réservation.
        </p>
      </div>
      <div className={styles['activation-codes-form-expiration-date']}>
        <DatePicker
          onChange={(event: ChangeEvent<HTMLInputElement>) => {
            if (isDateValid(event.target.value)) {
              setExpirationDate(
                formatShortDateForInput(
                  getLocalDepartementDateTimeFromUtc(
                    event.target.value,
                    departmentCode
                  )
                )
              )
            }
          }}
          label={'Date limite de validité'}
          className={styles['date-input']}
          name="activationCodesExpirationDatetime"
          minDate={getMinimumExpirationDatetime(minDate)}
        />
      </div>
      <div>
        <p>
          Vous ne pourrez modifier ni la quantité ni la date de validité après
          import.
        </p>
        <p>Souhaitez-vous valider l’opération ?</p>
      </div>
      <div className={styles['activation-codes-actions-button']}>
        <Button
          onClick={clearActivationCodes}
          variant={ButtonVariant.SECONDARY}
        >
          Retour
        </Button>
        <Button onClick={() => submitActivationCodes(expirationDate)}>
          Valider
        </Button>
      </div>
    </div>
  )
}
