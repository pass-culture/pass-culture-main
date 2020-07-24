import React, { useCallback, useState } from 'react'
import { Link } from 'react-router-dom'
import PropTypes from 'prop-types'

import { API_URL } from '../../../../utils/config'
import { Animation } from '../Animation/Animation'
import ContactSaved from '../ContactSaved/ContactSaved'
import { handleCheckEmailFormat } from '../utils/checkEmailFormat'

const EligibleSoon = ({ birthDate, postalCode }) => {
  const [emailValue, setEmailValue] = useState('')
  const [hasSubmitted, setHasSubmitted] = useState(false)

  const handleEmailInputChange = useCallback(event => {
    const newEmailValue = event.target.value
    setEmailValue(newEmailValue)
  }, [])

  const handleSubmit = useCallback(
    event => {
      event.preventDefault()
      const birthDateSplit = birthDate.split('/')
      const birthDateISO = birthDateSplit[2] + '-' + birthDateSplit[1] + '-' + birthDateSplit[0]
      const departmentCode = postalCode.substr(0, 2)

      const userInformations = {
        email: emailValue,
        dateOfBirth: birthDateISO,
        departmentCode: departmentCode,
      }

      return fetch(`${API_URL}/mailing-contacts`, {
        body: JSON.stringify(userInformations),
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        method: 'POST',
      }).then(response => {
        if (response.status !== 201) {
          throw new Error("Erreur lors de l'enregistrement de l'adresse e-mail")
        }

        setHasSubmitted(true)
      })
    },
    [emailValue, birthDate, postalCode]
  )

  const isEmailValid = handleCheckEmailFormat(emailValue)

  return !hasSubmitted ? (
    <main className="eligible-soon-page">
      <div className="animation-text-container">
        <Animation
          name="ineligible-under-eighteen-animation"
          speed={0.7}
        />
        <h2>
          {'Plus que quelques mois d’attente !'}
        </h2>
        <div className="information-text">
          {
            'Pour profiter du pass Culture, tu dois avoir 18 ans. Entre ton adresse email : nous t’avertirons dès que tu seras éligible.'
          }
        </div>
      </div>
      <div className="buttons-container">
        <form onSubmit={handleSubmit}>
          <input
            onChange={handleEmailInputChange}
            placeholder="Adresse email"
            type="email"
            value={emailValue}
          />
          <button
            className="submit-button"
            disabled={!isEmailValid}
            type="submit"
          >
            {'Rester en contact'}
          </button>
        </form>
        <Link to="/beta">
          {'Retourner à l’accueil'}
        </Link>
      </div>
    </main>
  ) : (
    <ContactSaved />
  )
}

EligibleSoon.propTypes = {
  birthDate: PropTypes.string.isRequired,
  postalCode: PropTypes.string.isRequired,
}

export default EligibleSoon
