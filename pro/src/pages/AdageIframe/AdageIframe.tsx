import * as React from 'react'
import './index.scss'

import { App } from './app/App'
import { AlgoliaQueryContextProvider } from './app/providers'

const AdageIframe = () => {
  return (
    <AlgoliaQueryContextProvider>
      <App />
    </AlgoliaQueryContextProvider>
  )
}

export default AdageIframe
