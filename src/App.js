import React from 'react'

import Header from './components/layout/Header'
import Modal from './components/layout/Modal'
import Splash from './components/layout/Splash'

const App = ({ children }) => {
  return (
    <div className="app">
      <Header />
      {children}
      <Modal />
      <Splash />
    </div>
  )
}

export default App
