import { FormikProvider, useFormik } from 'formik'
import React, { useId, useState } from 'react'

import { apiContremarque } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'
import { GetBookingResponse } from 'apiClient/v2'
import { Layout } from 'app/App/layout/Layout'
import { HeadlineOfferContextProvider } from 'commons/context/HeadlineOfferContext/HeadlineOfferContext'
import { HeadlineOfferBanner } from 'components/HeadlineOfferBanner/HeadlineOfferBanner'
import { Button } from 'ui-kit/Button/Button'
import { Callout } from 'ui-kit/Callout/Callout'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'

import { BookingDetails } from './BookingDetails'
import { ButtonInvalidateToken } from './ButtonInvalidateToken'
import styles from './Desk.module.scss'
import { DeskInputMessage } from './DeskInputMessage/DeskInputMessage'
import { getBookingFailure } from './getBookingFailure'
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

  const errorId = useId()
  const successId = useId()

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

    try {
      await apiContremarque.patchBookingUseByToken(formValues.token)
      onSubmitSuccess('Contremarque validée !')
    } catch (error) {
      if (isErrorAPIError(error)) {
        setMessage({
          message: error.body['global'],
          variant: MESSAGE_VARIANT.ERROR,
        })
      }
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
      try {
        const response = await apiContremarque.getBookingByTokenV2(token)
        setBooking(response)
        setMessage({
          message: 'Coupon vérifié, cliquez sur "Valider" pour enregistrer',
          variant: MESSAGE_VARIANT.DEFAULT,
        })
      } catch (e) {
        if (isErrorAPIError(e)) {
          const failure = getBookingFailure(e)
          setIsTokenValidated(failure.isTokenValidated)
          setBooking(null)
          setMessage({
            message: failure.message,
            variant: MESSAGE_VARIANT.ERROR,
          })
        }
      }
    }
  }

  const onSubmitSuccess = (successMessage: string) => {
    setMessage({
      message: successMessage,
      variant: MESSAGE_VARIANT.SUCCESS,
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

    try {
      await apiContremarque.patchBookingKeepByToken(token)
      onSubmitSuccess('Contremarque invalidée !')
    } catch (error) {
      if (isErrorAPIError(error)) {
        const failure = getBookingFailure(error)
        setIsTokenValidated(failure.isTokenValidated)
        setBooking(null)
        setMessage({
          message: failure.message,
          variant: MESSAGE_VARIANT.ERROR,
        })
      }
    }
  }

  return (
    <HeadlineOfferContextProvider>
      <Layout mainHeading="Guichet" mainBanner={<HeadlineOfferBanner />}>
        <p className={styles.advice}>
          Saisissez les contremarques présentées par les bénéficiaires afin de
          les valider ou de les invalider.
        </p>
        <FormikProvider value={formik}>
          <form onSubmit={formik.handleSubmit} className={styles['desk-form']}>
            <TextInput
              label="Contremarque"
              name="token"
              onChange={handleOnChangeToken}
              description="Format : 6 caractères alphanumériques en majuscules. Par exemple : AZE123"
              value={token}
              classNameLabel={styles['desk-form-label']}
              className={styles['desk-form-input']}
              isOptional
              aria-describedby={`${successId} ${errorId}`}
            />

            <div role="status">
              {booking && <BookingDetails booking={booking} />}
            </div>

            <div className={styles['desk-button']}>
              {isTokenValidated ? (
                <ButtonInvalidateToken
                  onConfirm={() => handleSubmitInvalidate(token)}
                />
              ) : (
                <Button
                  type="submit"
                  disabled={formik.isSubmitting || !booking}
                >
                  Valider la contremarque
                </Button>
              )}
            </div>

            <div role="alert" id={errorId}>
              {message.variant === MESSAGE_VARIANT.ERROR && (
                <DeskInputMessage message={message.message} isError />
              )}
            </div>
            <div role="status" id={successId}>
              {message.variant === MESSAGE_VARIANT.SUCCESS && (
                <DeskInputMessage message={message.message} />
              )}
            </div>

            {message.variant === MESSAGE_VARIANT.DEFAULT && (
              <DeskInputMessage message={message.message} />
            )}

            <Callout
              links={[
                {
                  href: 'https://aide.passculture.app/hc/fr/articles/4416062183569--Acteurs-Culturels-Modalités-de-retrait-et-CGU',
                  label: 'Modalités de retrait et CGU',
                  isExternal: true,
                },
              ]}
              className={`${styles['desk-callout']}`}
              title="N’oubliez pas de vérifier l’identité du bénéficiaire avant de valider la contremarque."
            >
              Les pièces d’identité doivent impérativement être présentées
              physiquement. Merci de ne pas accepter les pièces d’identité au
              format numérique.
            </Callout>
          </form>
        </FormikProvider>
      </Layout>
    </HeadlineOfferContextProvider>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = Desk
