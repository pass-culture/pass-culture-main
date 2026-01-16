import type React from 'react'
import { useEffect, useId, useRef, useState } from 'react'
import { useForm } from 'react-hook-form'

import { api } from '@/apiClient/api'
import { isErrorAPIError } from '@/apiClient/helpers'
import type { GetBookingResponse } from '@/apiClient/v1'
import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { HeadlineOfferContextProvider } from '@/commons/context/HeadlineOfferContext/HeadlineOfferContext'
import { Banner } from '@/design-system/Banner/Banner'
import { TextInput } from '@/design-system/TextInput/TextInput'
import fullLinkIcon from '@/icons/full-link.svg'
import { Button } from '@/ui-kit/Button/Button'

import { BookingDetails } from './BookingDetails'
import { ButtonInvalidateToken } from './ButtonInvalidateToken'
import styles from './Desk.module.scss'
import { DeskInputMessage } from './DeskInputMessage/DeskInputMessage'
import { getBookingFailure } from './getBookingFailure'
import { type ErrorMessage, MESSAGE_VARIANT } from './types'
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

  const tokenInputRef = useRef<HTMLInputElement | null>(null)

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
      await api.patchBookingUseByToken(formValues.token)

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
        const response = await api.getBookingByToken(token)
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
      await api.patchBookingKeepByToken(token)
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
    } finally {
      tokenInputRef.current?.focus()
    }
  }
  const tokenRegister = register('token')
  return (
    <HeadlineOfferContextProvider>
      <BasicLayout mainHeading="Guichet">
        <p className={styles.advice}>
          Saisissez les contremarques présentées par les bénéficiaires afin de
          les valider ou de les invalider.
        </p>
        <div className={styles['desk-form-wrapper']}>
          <div className={styles['desk-form']}>
            <form onSubmit={handleSubmit(onSubmit)}>
              <div className={styles['desk-form-input']}>
                <TextInput
                  {...tokenRegister}
                  label="Contremarque"
                  onChange={handleOnChangeToken}
                  description="Format : 6 caractères alphanumériques en majuscules. Par exemple : AZE123"
                  describedBy={statusId}
                  autoComplete="off"
                  ref={(input) => {
                    tokenRegister.ref(input)
                    tokenInputRef.current = input
                  }}
                  required
                  requiredIndicator="explicit"
                />
              </div>

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

              {/** biome-ignore lint/a11y/useSemanticElements: We want a `role="status"` here, not an `<output />`. */}
              <div role="status" id={statusId}>
                <DeskInputMessage
                  message={message.message}
                  variant={message.variant}
                />
              </div>
            </form>
          </div>
          <div className={`${styles['desk-callout']}`}>
            <Banner
              actions={[
                {
                  href: 'https://aide.passculture.app/hc/fr/articles/4416062183569--Acteurs-Culturels-Modalités-de-retrait-et-CGU',
                  label: 'Modalités de retrait et CGU',
                  isExternal: true,
                  type: 'link',
                  icon: fullLinkIcon,
                  iconAlt: 'Nouvelle fenêtre',
                },
              ]}
              title="N’oubliez pas de vérifier l’identité du bénéficiaire avant de valider la contremarque."
              description="Les pièces d’identité doivent impérativement être présentées physiquement. Merci de ne pas accepter les pièces d’identité au format numérique."
            />
          </div>
        </div>
      </BasicLayout>
    </HeadlineOfferContextProvider>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = Desk
