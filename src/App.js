import React from 'react'

import Modal from './components/layout/Modal'
import Splash from './components/layout/Splash'

import { ROOT_PATH } from './utils/config'


const App = ({ children }) => {
  return (
    <div className="app">
      {children}
      <Modal />
      <Splash />
      <img src={`${ROOT_PATH}/beta.png`} className='beta' alt='beta' srcset={`${ROOT_PATH}/beta@2x.png`} />
    </div>
  )
}

export default App
