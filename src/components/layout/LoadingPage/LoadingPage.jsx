import React from 'react'

import AbsoluteFooterContainer from '../AbsoluteFooter/AbsoluteFooterContainer'
import LoadingAnimation from './LoadingAnimation/LoadingAnimation'

const LoadingPage = () => (
  <div className="loading-page">
    <LoadingAnimation />
    <p>
      {'Chargement en cours…'}
    </p>
    <AbsoluteFooterContainer
      areDetailsVisible={false}
      borderTop
      id="deck-footer"
    />
  </div>
)

export default LoadingPage
