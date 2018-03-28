import React from 'react'
import { connect } from 'react-redux'

import Modal from './components/Modal'
import MenuButton from './components/layout/MenuButton'

const App = ({ children, user }) => {
  return (
    <div className='app'>
      {children}
      {user && <MenuButton />}
      <Modal />
    </div>
  )
}

export default connect(
  state => ({
    user: state.user
  })
)(App)
