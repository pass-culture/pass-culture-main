import React, { useCallback } from 'react'
import {
  APP_NATIVE_DYNAMIC_LINK,
  ANDROID_APP_ID,
  IOS_APP_STORE_ID,
  IOS_APP_ID,
} from '../../../../utils/config'

import { Animation } from '../Animation/Animation'

const setEmailUrl = `${APP_NATIVE_DYNAMIC_LINK}?link=https://passcultureapptesting.page.link/set-email&apn=${ANDROID_APP_ID}&isi=${IOS_APP_STORE_ID}&ibi=${IOS_APP_ID}&ofl=https://pass.culture.fr/nosapplications/`

const SignUpFromNativeApp = () => {
  const handleClick = useCallback(() => window.open(setEmailUrl, '_blank'), [])

  return (
    <main className="eligible-page">
      <div className="animation-text-container">
        <Animation
          name="eligible-animation"
          speed={0.6}
        />
        <div className="eligible-text">
          {`Télécharge l'application !`}
        </div>
        <div className="information-text">
          {`Pour réaliser ton inscripion, télécharge l'application pass Culture depuis les stores !`}
        </div>
      </div>

      <div className="buttons-container">
        <button
          className="eligible-sign-up-button"
          onClick={handleClick}
          type="button"
        >
          {'Télécharger l’application'}
        </button>
      </div>
    </main>
  )
}

export default SignUpFromNativeApp
