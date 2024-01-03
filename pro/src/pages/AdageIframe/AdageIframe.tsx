import * as React from 'react'
import './index.scss'

import { App } from './app/App'

const AdageIframe = () => {
  return <App />
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = AdageIframe
