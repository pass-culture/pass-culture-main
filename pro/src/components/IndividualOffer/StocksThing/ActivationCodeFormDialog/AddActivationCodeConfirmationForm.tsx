import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { DatePicker } from 'ui-kit/formV2/DatePicker/DatePicker'

import styles from './ActivationCodeFormDialog.module.scss'
import { UseFormSetValue } from 'react-hook-form'
import { isDateValid, FORMAT_ISO } from 'commons/utils/date'
import { ChangeEvent } from 'react'
import { format } from 'date-fns'

interface AddActivationCodeConfirmationFormProps {
  unsavedActivationCodes: string[] | undefined
  clearActivationCodes: () => void
  submitActivationCodes: () => void
  today: Date
  minExpirationDate: Date | null
  setValue: UseFormSetValue<any>
}

export const AddActivationCodeConfirmationForm = ({
  unsavedActivationCodes,
  clearActivationCodes,
  submitActivationCodes,
  today,
  minExpirationDate,
  setValue,
}: AddActivationCodeConfirmationFormProps) => {
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
          value={format(new Date(), FORMAT_ISO)}
          onChange={(event: ChangeEvent<HTMLInputElement>) => {
            if (isDateValid(event.target.value)) {
              setValue('activationCodesExpirationDatetime', event.target.value)
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
        <Button onClick={submitActivationCodes}>Valider</Button>
      </div>
    </div>
  )
}
