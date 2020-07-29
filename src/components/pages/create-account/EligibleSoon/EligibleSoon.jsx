import PropTypes from 'prop-types'
import React, { useCallback, useState } from 'react'
import { Link } from 'react-router-dom'

import { API_URL } from '../../../../utils/config'
import Icon from '../../../layout/Icon/Icon'
import ContactSaved from '../ContactSaved/ContactSaved'
import { checkIfEmailIsValid } from '../domain/checkIfEmailIsValid'

const HYPHEN = '-'

const EligibleSoon = ({ birthDate, body, postalCode, title, visual }) => {
  const [emailValue, setEmailValue] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [hasContactBeenSaved, setHasContactBeenSaved] = useState(false)

  const handleEmailInputChange = useCallback(event => {
    const newEmailValue = event.target.value
    setEmailValue(newEmailValue)
  }, [])

  const handleSubmit = useCallback(
    event => {
      event.preventDefault()
      setIsSubmitting(true)
      const birthDateSplit = birthDate.split('/')
      const birthDateISO =
        birthDateSplit[2] + HYPHEN + birthDateSplit[1] + HYPHEN + birthDateSplit[0]
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
        setIsSubmitting(false)
        if (response.status !== 201) {
          setHasContactBeenSaved(false)
          throw new Error("Erreur lors de l'enregistrement de l'adresse e-mail")
        }

        setHasContactBeenSaved(true)
      })
    },
    [birthDate, emailValue, postalCode]
  )

  const isEmailValid = checkIfEmailIsValid(emailValue)

  return hasContactBeenSaved ? (
    <ContactSaved />
  ) : (
    <main className="eligible-soon-page">
      <div className="animation-text-container">
        {visual}
        <h1>
          {title}
        </h1>
        <div className="information-text">
          {body}
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
            {isSubmitting ? <Icon svg="icon-eligible-spinner" /> : 'Rester en contact'}
          </button>
        </form>
        <Link to="/beta">
          {'Retourner à l’accueil'}
        </Link>
      </div>
    </main>
  )
}

EligibleSoon.propTypes = {
  birthDate: PropTypes.string.isRequired,
  body: PropTypes.string.isRequired,
  postalCode: PropTypes.string.isRequired,
  title: PropTypes.string.isRequired,
  visual: PropTypes.element.isRequired,
}

export default EligibleSoon
