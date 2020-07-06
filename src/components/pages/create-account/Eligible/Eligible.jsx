import React, { useCallback } from 'react'
import { Link } from 'react-router-dom'

import { ID_CHECK_URL } from '../../../../utils/config'
import { Animation } from '../Animation/Animation'
import { getReCaptchaToken } from '../utils/recaptcha'

const Eligible = () => {
  const handleClick = useCallback(() =>
    getReCaptchaToken().then(
      token => (window.location.href = `${ID_CHECK_URL}?licence_token=${token}`)
    )
  )

  return (
    <main className="eligible-page">
      <div className="animation-text-container">
        <Animation
          name="eligible-animation"
          speed={0.6}
        />
        <div className="eligible-text">
          {'Tu es éligible !'}
        </div>
      </div>
      <div className="buttons-container">
        <button
          className="eligible-sign-up-button"
          onClick={handleClick}
          type="button"
        >
          {'Commencer l’inscription'}
        </button>
        <Link
          className="home-page-link"
          to="/beta"
        >
          {'Retourner à l’accueil'}
        </Link>
      </div>
    </main>
  )
}

export default Eligible
