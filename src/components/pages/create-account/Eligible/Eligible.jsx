import React, { useCallback } from 'react'
import { getReCatchaToken } from '../utils/recaptcha'
import { ID_CHECK_URL } from '../../../../utils/config'

const Eligible = () => {
  const handleClick = useCallback(() =>
    getReCatchaToken().then(
      token => (window.location.href = `${ID_CHECK_URL}?licence_token=${token}`)
    )
  )

  return (
    <main>
      {' Eligible '}
      <button
        onClick={handleClick}
        style={{ color: 'black' }}
        type="submit"
      >
        {"Commencer l'inscription"}
      </button>
    </main>
  )
}

export default Eligible
