import cx from 'classnames'
import { FormikProvider, useFormik } from 'formik'
import React, { useState } from 'react'

import { GetBookingResponse } from 'apiClient/v2'
import { AppLayout } from 'app/AppLayout'
import Callout from 'components/Callout/Callout'
import { SubmitButton, TextInput } from 'ui-kit'
import Titles from 'ui-kit/Titles/Titles'

import { submitValidate, getBooking, submitInvalidate } from './adapters'
import { BookingDetails } from './BookingDetails'
import { ButtonInvalidateToken } from './ButtonInvalidateToken'
import styles from './Desk.module.scss'
import { ErrorMessage, MESSAGE_VARIANT } from './types'
import { validateToken } from './validation'

interface FormValues {
  token: string
}

export const Desk = (): JSX.Element => {
  const [token, setToken] = useState('')
  const [isTokenValidated, setIsTokenValidated] = useState(false)
  const [booking, setBooking] = useState<GetBookingResponse | null>(null)
  const [message, setMessage] = useState<ErrorMessage>({
    message: 'Saisissez une contremarque',
    variant: MESSAGE_VARIANT.DEFAULT,
  })

  const resetMessage = () => {
    setMessage({
      message: 'Saisissez une contremarque',
      variant: MESSAGE_VARIANT.DEFAULT,
    })
  }

  const onSubmit = async (formValues: FormValues) => {
    setMessage({
      message: 'Validation en cours...',
      variant: MESSAGE_VARIANT.DEFAULT,
    })

    const validateResponse = await submitValidate(formValues.token)

    if (validateResponse.error) {
      setMessage(validateResponse.error)
    } else {
      onSubmitSuccess('Contremarque validée !')
    }
  }

  const initialValues = {
    token: '',
  }

  const formik = useFormik({
    initialValues,
    onSubmit,
  })

  const handleOnChangeToken = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    formik.handleChange(event)
    const inputValue = event.target.value.toUpperCase()
    // QRCODE return a prefix that we want to ignore.
    const token = inputValue.split(':').reverse()[0]

    setToken(token)
    setIsTokenValidated(false)
    setMessage({
      message: 'Vérification...',
      variant: MESSAGE_VARIANT.DEFAULT,
    })

    const tokenErrorMessage = validateToken(token)
    if (tokenErrorMessage !== false) {
      setMessage(tokenErrorMessage)
      setBooking(null)
    } else {
      resetMessage()
      const responseBooking = await getBooking(token)

      if (responseBooking.error) {
        setIsTokenValidated(responseBooking.error.isTokenValidated)
        setBooking(null)
        setMessage(responseBooking.error)
      }

      if (responseBooking.booking) {
        setBooking(responseBooking.booking)
        setMessage({
          message: 'Coupon vérifié, cliquez sur "Valider" pour enregistrer',
          variant: MESSAGE_VARIANT.DEFAULT,
        })
      }
    }
  }

  const onSubmitSuccess = (successMessage: string) => {
    setMessage({
      message: successMessage,
      variant: MESSAGE_VARIANT.DEFAULT,
    })
    setIsTokenValidated(false)
    setToken('')
    setBooking(null)
  }

  const handleSubmitInvalidate = async (token: string) => {
    setMessage({
      message: 'Invalidation en cours...',
      variant: MESSAGE_VARIANT.DEFAULT,
    })

    const submitResponse = await submitInvalidate(token)

    if (submitResponse.error) {
      setMessage(submitResponse.error)
    } else {
      onSubmitSuccess('Contremarque invalidée !')
    }
  }

  return (
    <AppLayout>
      <Titles title="Guichet" />
      <p className={styles.advice}>
        Saisissez les contremarques présentées par les bénéficiaires afin de les
        valider ou de les invalider.
      </p>
      <FormikProvider value={formik}>
        <form onSubmit={formik.handleSubmit} className={styles['desk-form']}>
          <TextInput
            label="Contremarque"
            name="token"
            onChange={handleOnChangeToken}
            placeholder="ex : AZE123"
            value={token}
            classNameLabel={styles['desk-form-label']}
            className={styles['desk-form-input']}
            hideFooter
          />

          {booking && <BookingDetails booking={booking} />}

          <div className={styles['desk-button']}>
            {isTokenValidated ? (
              <ButtonInvalidateToken
                onConfirm={() => handleSubmitInvalidate(token)}
              />
            ) : (
              <SubmitButton disabled={formik.isSubmitting || !booking}>
                Valider la contremarque
              </SubmitButton>
            )}
          </div>

          <div
            aria-live="assertive"
            aria-relevant="all"
            className={cx(styles['desk-message'], {
              [styles['error']]: message.variant === MESSAGE_VARIANT.ERROR,
            })}
            data-testid="desk-message"
          >
            {message.message}
          </div>

          <Callout
            links={[
              {
                href: 'https://aide.passculture.app/hc/fr/articles/4416062183569--Acteurs-Culturels-Modalités-de-retrait-et-CGU',
                label: 'Modalités de retrait et CGU',
                isExternal: true,
              },
            ]}
            className={`${styles['desk-callout']}`}
            title=" N’oubliez pas de vérifier l’identité du bénéficiaire avant de
            valider la contremarque."
          >
            Les pièces d’identité doivent impérativement être présentées
            physiquement. Merci de ne pas accepter les pièces d’identité au
            format numérique.
          </Callout>
        </form>
      </FormikProvider>
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = Desk
