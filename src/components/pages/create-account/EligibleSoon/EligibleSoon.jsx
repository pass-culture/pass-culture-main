import React, { useCallback, useState } from 'react'
import { Link } from 'react-router-dom'

import { Animation } from '../Animation/Animation'
import { handleCheckEmailFormat } from '../utils/checkEmailFormat'

const EligibleSoon = () => {
  const [emailValue, setEmailValue] = useState()

  const handleEmailInputChange = useCallback(event => {
      const newEmailValue = event.target.value
      setEmailValue(newEmailValue)
    }, []
  )

  const isEmailValid = handleCheckEmailFormat(emailValue)

  return (
    <main className="eligible-soon-page">
      <div className="animation-text-container">
        <Animation
          name="ineligible-over-eighteen-animation"
          speed={0.7}
        />
        <h2>
          {'Plus que quelques mois d’attente !'}
        </h2>
        <div className="information-text">
          {'Pour profiter du pass Culture, tu dois avoir 18 ans. Entre ton adresse email : nous t’avertirons dès que tu seras éligible.'}
        </div>
      </div>
      <div className="buttons-container">
        <form action="/verification-eligibilite/gardons-contact">
          <input
            onChange={handleEmailInputChange}
            placeholder="Adresse email"
            type="email"
          />
          <button
            className="submit-button"
            disabled={!isEmailValid}
            type="submit"
          >
            {'Rester en contact'}
          </button>
        </form>
        <Link
          to="/beta"
        >
          {'Retourner à l’accueil'}
        </Link>
      </div>
    </main>
  )
}

export default EligibleSoon
