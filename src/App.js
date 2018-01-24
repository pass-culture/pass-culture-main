import React from 'react'

import Header from './components/Header'
import Menu from './components/Menu'
import Modal from './components/Modal'

const App = ({ children }) => {
  return (
    <div className='app'>
      <Header />
      {children}
      <Menu />
      <Modal />
    </div>
  )
}

export default App
