import * as React from 'react'
import './index.scss'

import { App } from './app/App'
import { AlgoliaQueryContextProvider } from './app/providers'
import { FeaturesContextProvider } from './app/providers/FeaturesContextProvider'

const AdageIframe = () => {
  return (
    <FeaturesContextProvider>
      <AlgoliaQueryContextProvider>
        <App />
      </AlgoliaQueryContextProvider>
    </FeaturesContextProvider>
  )
}

export default AdageIframe
