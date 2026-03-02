import { yupResolver } from '@hookform/resolvers/yup'
import type React from 'react'
import { useEffect, useId, useRef, useState } from 'react'
import { useForm } from 'react-hook-form'

import { api } from '@/apiClient/api'
import { isErrorAPIError } from '@/apiClient/helpers'
import type { GetBookingResponse } from '@/apiClient/v1'
import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { HeadlineOfferContextProvider } from '@/commons/context/HeadlineOfferContext/HeadlineOfferContext'
import { yup } from '@/commons/utils/yup'
import { Banner } from '@/design-system/Banner/Banner'
import { Button } from '@/design-system/Button/Button'
import { TextInput } from '@/design-system/TextInput/TextInput'
import fullLinkIcon from '@/icons/full-link.svg'

import { BookingDetails } from './BookingDetails'
import { ButtonInvalidateToken } from './ButtonInvalidateToken'
import styles from './Desk.module.scss'
import { getBookingFailure } from './getBookingFailure'

interface FormValues {
  token: string
}

const TOKEN_MAX_LENGTH = 6
const VALID_TOKEN_SYNTAX = /^[A-Z0-9]+$/

export const Desk = (): JSX.Element => {
  const [isTokenValidated, setIsTokenValidated] = useState(false)
  const [booking, setBooking] = useState<GetBookingResponse | null>(null)

  const statusId = useId()

  const tokenInputRef = useRef<HTMLInputElement | null>(null)

  const hookForm = useForm<FormValues>({
    mode: 'onChange', // important
    defaultValues: { token: '' },
    resolver: yupResolver(
      yup.object({
        token: yup
          .string()
          .required('Saisissez une contremarque')
          .length(6, 'La contremarque doit contenir 6 caractères')
          .matches(
            /^[A-Z0-9]+$/,
            'Caractères alphanumériques en majuscules (A–Z, 0–9)'
          ),
      })
    ),
  })

  const {
    register,
    handleSubmit,
    setFocus,
    trigger,
    getValues,
    setValue,
    setError,
    watch,
    formState: { errors, isValid, isSubmitting },
  } = hookForm

  useEffect(() => {
    setFocus('token')
  }, [setFocus])

  const onSubmit = async (formValues: FormValues) => {
    try {
      await api.patchBookingUseByToken(formValues.token)

      //  resetField('token')
      setBooking(null)
    } catch (error) {
      if (isErrorAPIError(error)) {
        setError('token', { message: error.body['global'] })
      }
    }
  }

  const handleOnChangeToken = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const inputValue = event.target.value.toUpperCase()
    const token = inputValue.split(':').reverse()[0]

    setValue('token', token, { shouldValidate: true })
    // 🚀 Only continue if regex is valid
    if (!isValid) {
      setBooking(null)
      return
    }

    // ✅ Safe to call API
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

  const handleSubmitInvalidate = async (token: string) => {
    try {
      await api.patchBookingKeepByToken(token)
      setIsTokenValidated(false)
      //  resetField('token')
    } catch (error) {
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
        <div className={styles['desk-form-wrapper']}>
          <div className={styles['desk-form']}>
            <form onSubmit={handleSubmit(onSubmit)}>
              <div className={styles['desk-form-input']}>
                <TextInput
                  {...register('token')}
                  value={watch('token')}
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
              </div>

              {booking && <BookingDetails booking={booking} />}

              <div className={styles['desk-button']}>
                {isTokenValidated ? (
                  <ButtonInvalidateToken
                    onConfirm={() => handleSubmitInvalidate(getValues('token'))}
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
          </div>
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
      </BasicLayout>
    </HeadlineOfferContextProvider>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = Desk
