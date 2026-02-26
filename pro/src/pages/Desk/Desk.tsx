import { yupResolver } from '@hookform/resolvers/yup'
import type React from 'react'
import { useEffect, useId, useRef, useState } from 'react'
import { useForm } from 'react-hook-form'

import { api } from '@/apiClient/api'
import { isErrorAPIError } from '@/apiClient/helpers'
import type { GetBookingResponse } from '@/apiClient/v1'
import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { HeadlineOfferContextProvider } from '@/commons/context/HeadlineOfferContext/HeadlineOfferContext'
import { Banner } from '@/design-system/Banner/Banner'
import { Button } from '@/design-system/Button/Button'
import { TextInput } from '@/design-system/TextInput/TextInput'
import fullLinkIcon from '@/icons/full-link.svg'
import { Panel } from '@/ui-kit/Panel/Panel'

import { BookingDetails } from './BookingDetails'
import { ButtonInvalidateToken } from './ButtonInvalidateToken'
import styles from './Desk.module.scss'
import { getBookingFailure } from './getBookingFailure'
import { validationDeskSchema } from './validationDeskSchema'

interface FormValues {
  token: string
}

export const Desk = (): JSX.Element => {
  const [isTokenValidated, setIsTokenValidated] = useState(false)
  const [booking, setBooking] = useState<GetBookingResponse | null>(null)

  const statusId = useId()

  const tokenInputRef = useRef<HTMLInputElement | null>(null)

  const hookForm = useForm<FormValues>({
    mode: 'onChange', // important
    defaultValues: { token: '' },
    resolver: yupResolver(validationDeskSchema),
  })

  const {
    register,
    handleSubmit,
    setValue,
    setError,
    watch,
    resetField,
    formState: { errors, isValid, isSubmitting },
  } = hookForm

  const token = watch('token')

  useEffect(() => {
    if (!isValid) {
      setBooking(null)
      return
    }

    const fetchBooking = async () => {
      try {
        const response = await api.getBookingByToken(token)
        setBooking(response)
      } catch (e) {
        if (isErrorAPIError(e)) {
          const failure = getBookingFailure(e)
          setIsTokenValidated(failure.isTokenValidated)
          setBooking(null)
          setError('token', { message: failure.message })
        }
      }
    }

    fetchBooking()
  }, [token, isValid, setError])

  const handleOnChangeToken = (event: React.ChangeEvent<HTMLInputElement>) => {
    const inputValue = event.target.value.toUpperCase()
    const token = inputValue.split(':').reverse()[0]

    setValue('token', token, { shouldValidate: true })
  }

  const handleSubmitValidate = async (formValues: FormValues) => {
    try {
      await api.patchBookingUseByToken(formValues.token)

      setBooking(null)
      resetField('token')
    } catch (error) {
      console.log('validate', error)

      if (isErrorAPIError(error)) {
        setError('token', { message: error.body['global'] })
      }
    }
  }

  const handleSubmitInvalidate = async (token: string) => {
    try {
      await api.patchBookingKeepByToken(token)
      setIsTokenValidated(false)
      resetField('token')
    } catch (error) {
      console.log('invalidate', error)
      if (isErrorAPIError(error)) {
        const failure = getBookingFailure(error)
        setIsTokenValidated(failure.isTokenValidated)
      }
    } finally {
      tokenInputRef.current?.focus()
    }
  }

  return (
    <HeadlineOfferContextProvider>
      <BasicLayout mainHeading="Guichet">
        <p className={styles.advice}>
          Saisissez les contremarques présentées par les bénéficiaires afin de
          les valider ou de les invalider.
        </p>
        <Panel>
          <div className={styles['desk-form-wrapper']}>
            <form onSubmit={handleSubmit(handleSubmitValidate)}>
              <div className={styles['desk-form']}>
                <TextInput
                  {...register('token')}
                  value={token}
                  label="Contremarque"
                  onChange={handleOnChangeToken}
                  description="Caractères alphanumériques en majuscules. Par exemple : AZE123"
                  describedBy={statusId}
                  autoComplete="off"
                  required
                  requiredIndicator="explicit"
                  maxCharactersCount={6}
                  error={errors?.token?.message}
                />

                {booking && <BookingDetails booking={booking} />}

                {isTokenValidated ? (
                  <ButtonInvalidateToken
                    onConfirm={() => handleSubmitInvalidate(token)}
                  />
                ) : (
                  <Button
                    type="submit"
                    disabled={isSubmitting || !booking}
                    isLoading={isSubmitting}
                    label="Valider la contremarque"
                  />
                )}
              </div>
            </form>
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
        </Panel>
      </BasicLayout>
    </HeadlineOfferContextProvider>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = Desk
