import PropTypes from 'prop-types'
import React, { useCallback, useState } from 'react'
import { Link } from 'react-router-dom'

import { API_URL } from '../../../../utils/config'
import Icon from '../../../layout/Icon/Icon'
import ContactSaved from '../ContactSaved/ContactSaved'
import { handleCheckEmailFormat } from '../utils/checkEmailFormat'

const IneligibleDepartment = ({ birthDate, postalCode }) => {
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
      const birthDateISO = birthDateSplit[2] + '-' + birthDateSplit[1] + '-' + birthDateSplit[0]
      const departmentCode = postalCode.substr(0, 2)

      return fetch(`${API_URL}/mailing-contacts`, {
        body: JSON.stringify({ email: emailValue, dateOfBirth: birthDateISO, departmentCode }),
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

  const isEmailValid = handleCheckEmailFormat(emailValue)

  return hasContactBeenSaved ? (
    <ContactSaved />
  ) : (
    <main className="eligible-soon-page">
      <div className="animation-text-container">
        <Icon svg="ineligible-department" />
        <h1>
          {'Bientôt disponible dans ton département !'}
        </h1>
        <div className="information-text">
          {
            'Entre ton adresse e-mail : nous te contacterons dès que le pass arrivera dans ton département'
          }
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

IneligibleDepartment.propTypes = {
  birthDate: PropTypes.string.isRequired,
  postalCode: PropTypes.string.isRequired,
}

export default IneligibleDepartment
