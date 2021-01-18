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
    <main className="eligible-soon-page">
      <div className="animation-text-container">
        <img
          alt=""
          src={`${ICONS_URL}/404.svg`}
        />
        <h1>
          {'Oups !'}
        </h1>
        <div className="information-text">
          <p>
            {'Cette page est indisponible pour le moment.'}
          </p>
          <p>
            {'Entre ton adresse email pour être prévenu dès que nous revenons en ligne.'}
          </p>
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
