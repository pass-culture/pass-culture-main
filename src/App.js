import React from 'react'
import { compose } from 'redux'

import withDebug from './components/hocs/withDebug'

import Modal from './components/layout/Modal'
import Splash from './components/layout/Splash'

import { ROOT_PATH } from './utils/config'


const App = ({ children }) => {
  return (
    <div className="app">
      {children}
      <img src={`${ROOT_PATH}/beta.png`} className='beta' alt='beta' srcSet={`${ROOT_PATH}/beta@2x.png`} />
      <Modal />
      <Splash />
    </div>
  )
}

// export default App
export default compose(withDebug)(App)
