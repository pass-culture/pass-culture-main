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

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = AdageIframe
