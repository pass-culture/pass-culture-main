import React from 'react'
import PropTypes from 'prop-types'

import Debug from './components/layout/Debug'
import Splash from './components/layout/Splash'

import { ROOT_PATH } from './utils/config'

const App = ({ children }) => (
  <Debug className="app">
    {children}
    <img
      alt="beta"
      className="beta"
      src={`${ROOT_PATH}/beta.png`}
      srcSet={`${ROOT_PATH}/beta@2x.png`}
    />
    <Splash />
  </Debug>
)

App.propTypes = {
  children: PropTypes.node.isRequired,
}

export default App
