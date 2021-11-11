import React from 'react'

import { Animation } from '../../pages/create-account/Animation/Animation'

const Loader = () => (
  <div className="loader">
    <Animation
      loop
      name="loading-animation"
    />
    <p className="loader-message">
      {'Chargement en cours…'}
    </p>
  </div>
)

export default Loader
