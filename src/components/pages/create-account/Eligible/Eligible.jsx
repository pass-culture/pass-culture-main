import React, { useCallback } from 'react'
import { getReCaptchaToken } from '../utils/recaptcha'
import { ID_CHECK_URL } from '../../../../utils/config'

const Eligible = () => {
  const handleClick = useCallback(() =>
    getReCaptchaToken().then(
      token => (window.location.href = `${ID_CHECK_URL}?licence_token=${token}`)
    )
  )

  return (
    <main>
      {' Eligible '}
      <button
        onClick={handleClick}
        type="submit"
      >
        {"Commencer l'inscription"}
      </button>
    </main>
  )
}

export default Eligible
