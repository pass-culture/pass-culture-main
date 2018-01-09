import React from 'react'

import Header from './components/Header'
import Modal from './components/Modal'

const App = ({ children }) => {
  return (
    <div className='app'>
      <Header />
      {children}
      <Modal />
    </div>
  )
}

export default App
