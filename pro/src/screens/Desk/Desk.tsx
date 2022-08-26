import cx from 'classnames'
import React, { useRef, useState } from 'react'

import TextInput from 'components/layout/inputs/TextInput/TextInput'
import Titles from 'components/layout/Titles/Titles'
import { Banner, Button } from 'ui-kit'

import { BookingDetails } from './BookingDetails'
import { ButtonInvalidateToken } from './ButtonInvalidateToken'
import styles from './Desk.module.scss'
import {
  IBooking,
  IDeskGetBookingResponse,
  IDeskProps,
  IDeskSubmitResponse,
  IErrorMessage,
  MESSAGE_VARIANT,
} from './types'
import { validateToken } from './validation'

const Desk = ({
  getBooking,
  submitInvalidate,
  submitValidate,
}: IDeskProps): JSX.Element => {
  const [token, setToken] = useState('')
  const [isTokenValidated, setIsTokenValidated] = useState(false)
  const [booking, setBooking] = useState<IBooking | null>(null)
  const [message, setMessage] = useState<IErrorMessage>({
    message: 'Saisissez une contremarque',
    variant: MESSAGE_VARIANT.DEFAULT,
  })
  const [disableSubmitValidate, setDisableSubmitValidate] = useState(true)
  const tokenInputRef = useRef<HTMLInputElement | null>(null)

  const resetMessage = () => {
    setMessage({
      message: 'Saisissez une contremarque',
      variant: MESSAGE_VARIANT.DEFAULT,
    })
  }

  const resetTokenField = () => {
    if (tokenInputRef.current !== null) {
      tokenInputRef.current.value = ''
      tokenInputRef.current.focus()
    }
    setDisableSubmitValidate(true)
  }

  const handleOnChangeToken = (event: React.ChangeEvent<HTMLInputElement>) => {
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
      getBooking(token).then((responseBooking: IDeskGetBookingResponse) => {
        if (responseBooking.error) {
          setIsTokenValidated(responseBooking.error.isTokenValidated)
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
    resetTokenField()
  }

  const handleSubmitValidate =
    (token: string) => (event: React.MouseEvent<HTMLButtonElement>) => {
      event.preventDefault()
      setMessage({
        message: 'Validation en cours...',
        variant: MESSAGE_VARIANT.DEFAULT,
      })

      submitValidate(token).then((submitResponse: IDeskSubmitResponse) => {
        if (submitResponse.error) {
          setMessage(submitResponse.error)
        } else {
          onSubmitSuccess('Contremarque validée !')
        }
      })
    }

  const handleSubmitInvalidate = (token: string) => {
    setMessage({
      message: 'Invalidation en cours...',
      variant: MESSAGE_VARIANT.DEFAULT,
    })
    submitInvalidate(token).then((submitResponse: IDeskSubmitResponse) => {
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
      <form className={styles['desk-form']}>
        <TextInput
          inputRef={tokenInputRef}
          label="Contremarque"
          name="token"
          onChange={handleOnChangeToken}
          placeholder="ex : AZE123"
          type="text"
          value={token}
        />

        <BookingDetails booking={booking} />

        <div className={styles['desk-button']}>
          {isTokenValidated ? (
            <ButtonInvalidateToken
              onConfirm={() => handleSubmitInvalidate(token)}
            />
          ) : (
            <Button
              disabled={disableSubmitValidate}
              onClick={handleSubmitValidate(token)}
              type="submit"
            >
              Valider la contremarque
            </Button>
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
    </div>
  )
}

export default Desk
