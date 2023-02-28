import * as React from 'react'
import './index.scss'

import { App } from './app/App'
import {
  AlgoliaQueryContextProvider,
  FiltersContextProvider,
} from './app/providers'
import { FeaturesContextProvider } from './app/providers/FeaturesContextProvider'

const AdageIframe = () => {
  return (
    <FeaturesContextProvider>
      <FiltersContextProvider>
        <AlgoliaQueryContextProvider>
          <App />
        </AlgoliaQueryContextProvider>
      </FiltersContextProvider>
    </FeaturesContextProvider>
  )
}

export default AdageIframe
