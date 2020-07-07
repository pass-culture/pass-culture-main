import React, { useEffect, useRef, useCallback } from 'react'
import { getReCaptchaToken } from '../utils/recaptcha'
import { ID_CHECK_URL } from '../../../../utils/config'
import { Link } from 'react-router-dom'
import lottie from 'lottie-web'

import animation from './eligible-animation.json'

const Eligible = () => {
  const animationContainer = useRef(null)

  const handleClick = useCallback(() =>
    getReCaptchaToken().then(
      token => (window.location.href = `${ID_CHECK_URL}?licence_token=${token}`)
    )
  )

  useEffect(() => {
    lottie
      .loadAnimation({
        container: animationContainer.current,
        renderer: 'svg',
        loop: false,
        autoplay: true,
        animationData: animation,
      })
      .setSpeed(0.7)
  }, [])

  return (
    <main className="eligible-page">
      <div className="animation-text-container">
        <div
          className="eligible-animation"
          ref={animationContainer}
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
