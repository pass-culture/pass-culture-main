import { useId } from 'react'
import { UseFormReturn } from 'react-hook-form'

import { useAnalytics } from 'app/App/analytics/firebase'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { StocksCalendarFormValues } from 'components/IndividualOffer/StocksEventCreation/form/types'
import { BaseInput } from 'ui-kit/form/shared/BaseInput/BaseInput'
import { FieldError } from 'ui-kit/form/shared/FieldError/FieldError'

import styles from './StocksCalendarLimitDates.module.scss'

export function StocksCalendarLimitDates({
  form,
}: {
  form: UseFormReturn<StocksCalendarFormValues>
}) {
  const { logEvent } = useAnalytics()

  const limitDateLabelId = useId()
  const limitDateErrorId = useId()
  const errorMessage = form.formState.errors.bookingLimitDateInterval?.message

  const bookingLimitDateIntervalRegister = form.register(
    'bookingLimitDateInterval'
  )

  return (
    <fieldset className={styles['container']}>
      <legend>
        <h2 className={styles['legend']}>Date limite de réservation</h2>
      </legend>

      <div className={styles['booking-date-limit']}>
        <div className={styles['booking-date-limit-row']}>
          <BaseInput
            type="number"
            step="1"
            hasError={Boolean(errorMessage)}
            className={styles['booking-date-limit-input']}
            id={limitDateLabelId}
            {...bookingLimitDateIntervalRegister}
            onBlur={async (e) => {
              await bookingLimitDateIntervalRegister.onBlur(e)

              if (form.getFieldState('bookingLimitDateInterval').isDirty) {
                logEvent(Events.UPDATED_BOOKING_LIMIT_DATE, {
                  from: location.pathname,
                  bookingLimitDateInterval: form.watch(
                    'bookingLimitDateInterval'
                  ),
                })
              }
            }}
          />

          <label
            className={styles['booking-date-limit-text']}
            htmlFor={limitDateLabelId}
          >
            jours avant le début de l’évènement
          </label>
        </div>

        <div
          role="alert"
          id={limitDateErrorId}
          className={styles['booking-date-limit-row-error']}
        >
          {errorMessage && (
            <FieldError name="bookingLimitDateInterval">
              {errorMessage}
            </FieldError>
          )}
        </div>
      </div>
    </fieldset>
  )
}
