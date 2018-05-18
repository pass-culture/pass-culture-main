import React from 'react'

import Debug from './components/layout/Debug'
import Modal from './components/layout/Modal'
import Splash from './components/layout/Splash'

import { ROOT_PATH } from './utils/config'


const App = ({ children }) => {
  return (
    <Debug className="app">
      {children}
      <img src={`${ROOT_PATH}/beta.png`} className='beta' alt='beta' srcSet={`${ROOT_PATH}/beta@2x.png`} />
      <Modal />
      <Splash />
    </Debug>
  )
}

export default App
