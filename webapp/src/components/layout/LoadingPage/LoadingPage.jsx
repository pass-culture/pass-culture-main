import React from 'react'

import { Animation } from '../../pages/create-account/Animation/Animation'

const LoadingPage = () => (
  <div className="loading-page">
    <Animation
      loop
      name="loading-animation"
    />
    <p>
      {'Chargement en cours…'}
    </p>
  </div>
)

export default LoadingPage
