import React from 'react'

import Modal from './components/Modal'
import Splash from './components/layout/Splash'

const App = ({ children }) => {
  return (
    <div className='app'>
      {children}
      <Modal />
      <Splash />
    </div>
  )
}

export default App
