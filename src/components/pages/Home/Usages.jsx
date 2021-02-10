import React from 'react'

import { steps, STEP_ID_USAGES } from './HomepageBreadcrumb'

const Usages = () => {
  return (
    <>
      <h2
        className="h-section-title"
        id={steps[STEP_ID_USAGES].hash}
      >
        {'Modalités d’usage'}
      </h2>

      <div className="h-section-row">
        {'1. Découvrir les offres éligibles pour votre structure'}
      </div>

      <div className="h-section-row">
        {'2. Comment créer ou synchroniser une offre physique'}
      </div>
    </>
  )
}

export default Usages
