import React, { useCallback, useState } from 'react'
import { Link } from 'react-router-dom'

import { FALLBACK_STORE_EMAIL_URL, ICONS_URL } from '../../../../utils/config'
import Icon from '../../../layout/Icon/Icon'
import ContactSaved from '../ContactSaved/ContactSaved'
import { checkIfEmailIsValid } from '../domain/checkIfEmailIsValid'

const IdCheckDisabled = () => {
  const [emailValue, setEmailValue] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [hasContactBeenSaved, setHasContactBeenSaved] = useState(false)

  const handleEmailInputChange = useCallback(event => {
    const newEmailValue = event.target.value
    setEmailValue(newEmailValue)
  }, [])

  const handleSubmit = useCallback(
    async event => {
      event.preventDefault()
      setIsSubmitting(true)

      try {
        const response = await fetch(FALLBACK_STORE_EMAIL_URL, {
          body: JSON.stringify({ email: emailValue }),
          headers: {
            'Content-Type': 'application/json',
          },
          method: 'POST',
        })
        if (response.ok) {
          setHasContactBeenSaved(true)
        }
      } catch (e) {
        setIsSubmitting(false)
      }
    },
    [emailValue]
  )

  const isEmailValid = checkIfEmailIsValid(emailValue)

  return hasContactBeenSaved ? (
    <ContactSaved />
  ) : (
    <main className="eligible-soon-page id-check-disabled-page">
      <div className="animation-text-container">
        <img
          alt=""
          src={`${ICONS_URL}/404.svg`}
        />
        <h1>
          {'Oups !'}
        </h1>
        <div className="information-text">
          {
            'Vous êtes très nombreux à solliciter le service. Pour être prévenu du suivi de ton dossier :'
          }
        </div>
        <a
          className="application-download submit-button"
          href="https://passcultureapp.page.link/home"
        >
          {"Télécharge l'application"}
        </a>
        <div className="information-text">
          {'Ou entre ton e-mail : nous te préviendrons dès que nous reviendrons en ligne !'}
        </div>
      </div>
      <div className="buttons-container">
        <form onSubmit={handleSubmit}>
          <input
            onChange={handleEmailInputChange}
            placeholder="Adresse e-mail"
            type="email"
            value={emailValue}
          />
          <div className="information-text legal-notice">
            <p>
              {
                "En cliquant sur \"Je veux rester informé\", j'accepte d'être contacté par e-mail lorsque l'inscription sera de nouveau disponible. Mon adresse ne sera pas utilisée à d'autres fins."
              }
            </p>
          </div>
          <button
            className="submit-button"
            disabled={!isEmailValid || isSubmitting}
            type="submit"
          >
            {isSubmitting ? <Icon svg="icon-eligible-spinner" /> : 'Je veux rester informé'}
          </button>
        </form>
        <Link to="/beta">
          {'Retourner à l’accueil'}
        </Link>
      </div>
    </main>
  )
}

export default IdCheckDisabled
