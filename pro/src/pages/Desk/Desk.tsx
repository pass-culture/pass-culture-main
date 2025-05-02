import React, { useEffect, useId, useState } from 'react'
import { useForm } from 'react-hook-form'

import { apiContremarque } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'
import { GetBookingResponse } from 'apiClient/v2'
import { Layout } from 'app/App/layout/Layout'
import { HeadlineOfferContextProvider } from 'commons/context/HeadlineOfferContext/HeadlineOfferContext'
import { Button } from 'ui-kit/Button/Button'
import { Callout } from 'ui-kit/Callout/Callout'
import { TextInput } from 'ui-kit/formV2/TextInput/TextInput'

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
  const [isTokenValidated, setIsTokenValidated] = useState(false)
  const [booking, setBooking] = useState<GetBookingResponse | null>(null)
  const [message, setMessage] = useState<ErrorMessage>({
    message: 'Saisissez une contremarque',
  })

  const statusId = useId()

  const hookForm = useForm({
    defaultValues: {
      token: '',
    },
    mode: 'onBlur',
  })

  const {
    register,
    handleSubmit,
    setFocus,
    resetField,
    getValues,
    setValue,
    formState: { isSubmitting },
  } = hookForm

  useEffect(() => {
    setFocus('token')
  }, [setFocus])

  const onSubmit = async (formValues: FormValues) => {
    setMessage({ message: 'Validation en cours...' })

    try {
      await apiContremarque.patchBookingUseByToken(formValues.token)

      setMessage({ message: 'Contremarque validée !' })
      resetField('token')
      setBooking(null)
    } catch (error) {
      if (isErrorAPIError(error)) {
        setMessage({
          message: error.body['global'],
          variant: MESSAGE_VARIANT.ERROR,
        })
      }
    }
  }

  const handleOnChangeToken = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const inputValue = event.target.value.toUpperCase()
    // QRCODE return a prefix that we want to ignore.
    const token = inputValue.split(':').reverse()[0]

    setValue('token', token)

    setMessage({
      message: 'Vérification...',
    })

    const tokenErrorMessage = validateToken(token)

    if (tokenErrorMessage) {
      setMessage(tokenErrorMessage)
      setBooking(null)
    } else {
      setMessage({ message: 'Saisissez une contremarque' })

      try {
        const response = await apiContremarque.getBookingByTokenV2(token)
        setBooking(response)
        setMessage({
          message: 'Coupon vérifié, cliquez sur "Valider" pour enregistrer',
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

  const handleSubmitInvalidate = async (token: string) => {
    setMessage({ message: 'Invalidation en cours...' })

    try {
      await apiContremarque.patchBookingKeepByToken(token)
      setMessage({ message: 'Contremarque invalidée !' })
      setIsTokenValidated(false)
      resetField('token')
    } catch (error) {
      if (isErrorAPIError(error)) {
        const failure = getBookingFailure(error)
        setIsTokenValidated(failure.isTokenValidated)
        setMessage({
          message: failure.message,
          variant: MESSAGE_VARIANT.ERROR,
        })
      }
    }
  }

  return (
    <HeadlineOfferContextProvider>
      <Layout mainHeading="Guichet">
        <p className={styles.advice}>
          Saisissez les contremarques présentées par les bénéficiaires afin de
          les valider ou de les invalider.
        </p>
        <div className={styles['desk-form-wrapper']}>
          <div className={styles['desk-form']}>
            <form onSubmit={handleSubmit(onSubmit)}>
              <TextInput
                {...register('token')}
                label="Contremarque"
                name="token"
                onChange={handleOnChangeToken}
                description="Format : 6 caractères alphanumériques en majuscules. Par exemple : AZE123"
                className={styles['desk-form-input']}
                aria-describedby={`${statusId}`}
                autoComplete="off"
              />

              {booking && <BookingDetails booking={booking} />}

              <div className={styles['desk-button']}>
                {isTokenValidated ? (
                  <ButtonInvalidateToken
                    onConfirm={() => handleSubmitInvalidate(getValues('token'))}
                  />
                ) : (
                  <Button type="submit" disabled={isSubmitting || !booking}>
                    Valider la contremarque
                  </Button>
                )}
              </div>

              <div role="status" id={statusId}>
                <DeskInputMessage
                  message={message.message}
                  variant={message.variant}
                />
              </div>
            </form>
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
            title="N’oubliez pas de vérifier l’identité du bénéficiaire avant de valider la contremarque."
          >
            Les pièces d’identité doivent impérativement être présentées
            physiquement. Merci de ne pas accepter les pièces d’identité au
            format numérique.
          </Callout>
        </div>
      </Layout>
    </HeadlineOfferContextProvider>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = Desk
