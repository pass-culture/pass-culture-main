import React from 'react'

import Modal from './components/Modal'

const App = ({ children }) => {
  return (
    <div className='app'>
      {children}
      <Modal />
    </div>
  )
}

export default App
