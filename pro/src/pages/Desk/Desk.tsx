import cx from 'classnames'
import { FormikProvider, useFormik } from 'formik'
import React, { useState } from 'react'

import { GetBookingResponse } from 'apiClient/v2'
import { Banner, SubmitButton, TextInput } from 'ui-kit'
import Titles from 'ui-kit/Titles/Titles'

import { submitValidate, getBooking, submitInvalidate } from './adapters'
import { BookingDetails } from './BookingDetails'
import { ButtonInvalidateToken } from './ButtonInvalidateToken'
import styles from './Desk.module.scss'
import {
  DeskGetBookingResponse,
  DeskSubmitResponse,
  ErrorMessage,
  MESSAGE_VARIANT,
} from './types'
import { validateToken } from './validation'

interface FormValues {
  token: string
}

const Desk = (): JSX.Element => {
  const [token, setToken] = useState('')
  const [isTokenValidated, setIsTokenValidated] = useState(false)
  const [booking, setBooking] = useState<GetBookingResponse | null>(null)
  const [message, setMessage] = useState<ErrorMessage>({
    message: 'Saisissez une contremarque',
    variant: MESSAGE_VARIANT.DEFAULT,
  })
  const [disableSubmitValidate, setDisableSubmitValidate] = useState(true)

  const resetMessage = () => {
    setMessage({
      message: 'Saisissez une contremarque',
      variant: MESSAGE_VARIANT.DEFAULT,
    })
  }

  const handleSubmitValidate = (formValues: FormValues) => {
    setDisableSubmitValidate(true)
    setMessage({
      message: 'Validation en cours...',
      variant: MESSAGE_VARIANT.DEFAULT,
    })

    submitValidate(formValues.token).then(
      (submitResponse: DeskSubmitResponse) => {
        if (submitResponse.error) {
          setMessage(submitResponse.error)
        } else {
          onSubmitSuccess('Contremarque validée !')
        }
      }
    )
  }

  const initialValues = {
    token: '',
  }

  const formik = useFormik({
    initialValues,
    onSubmit: handleSubmitValidate,
  })

  const handleOnChangeToken = (event: React.ChangeEvent<HTMLInputElement>) => {
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
      getBooking(token).then((responseBooking: DeskGetBookingResponse) => {
        if (responseBooking.error) {
          setIsTokenValidated(responseBooking.error.isTokenValidated)
          setBooking(null)
          setMessage(responseBooking.error)
        }
        if (responseBooking.booking) {
          setDisableSubmitValidate(false)
          setBooking(responseBooking.booking)
          setMessage({
            message: 'Coupon vérifié, cliquez sur "Valider" pour enregistrer',
            variant: MESSAGE_VARIANT.DEFAULT,
          })
        }
      })
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
    setDisableSubmitValidate(true)
  }

  const handleSubmitInvalidate = (token: string) => {
    setMessage({
      message: 'Invalidation en cours...',
      variant: MESSAGE_VARIANT.DEFAULT,
    })
    submitInvalidate(token).then((submitResponse: DeskSubmitResponse) => {
      if (submitResponse.error) {
        setMessage(submitResponse.error)
      } else {
        onSubmitSuccess('Contremarque invalidée !')
      }
    })
  }

  return (
    <div className={styles['desk-screen']}>
      <Titles title="Guichet" />
      <p className="advice">
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

          <BookingDetails booking={booking} />

          <div className={styles['desk-button']}>
            {isTokenValidated ? (
              <ButtonInvalidateToken
                onConfirm={() => handleSubmitInvalidate(token)}
              />
            ) : (
              <SubmitButton disabled={disableSubmitValidate}>
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
          <Banner
            links={[
              {
                href: 'https://aide.passculture.app/hc/fr/articles/4416062183569--Acteurs-Culturels-Modalités-de-retrait-et-CGU',
                linkTitle: 'En savoir plus',
              },
            ]}
            type="notification-info"
            className={styles['desk-banner']}
          >
            <strong>
              N’oubliez pas de vérifier l’identité du bénéficiaire avant de
              valider la contremarque.
            </strong>
            {
              ' Les pièces d’identité doivent impérativement être présentées physiquement. Merci de ne pas accepter les pièces d’identité au format numérique.'
            }
          </Banner>
        </form>
      </FormikProvider>
    </div>
  )
}

export default Desk
