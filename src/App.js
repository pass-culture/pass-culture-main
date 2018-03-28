import React from 'react'
import { connect } from 'react-redux'

import Modal from './components/Modal'

const App = ({ children, user }) => {
  return (
    <div className='app'>
      {children}
      <Modal />
    </div>
  )
}

export default connect(
  state => ({
    user: state.user
  })
)(App)
