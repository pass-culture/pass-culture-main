import React from 'react'
import LoadingAnimation from './LoadingAnimation/LoadingAnimation'

const LoadingPage = () => (
  <div className="loading-page">
    <LoadingAnimation />
    <p>
      {'Chargement en cours ...'}
    </p>
  </div>
)

export default LoadingPage
