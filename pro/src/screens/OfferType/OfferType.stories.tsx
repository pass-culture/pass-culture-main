import { createBrowserHistory } from 'history'
import React from 'react'
import { Router } from 'react-router'

import OfferType from './OfferType'

export default {
  title: 'screens/OfferType',
  component: OfferType,
}

const Template = () => {
  const history = createBrowserHistory()
  return (
    <>
      <div />
      <main className="container">
        <div className="page-content">
          <div className="after-notification-content">
            <Router history={history}>
              <OfferType />
            </Router>
          </div>
        </div>
      </main>
      <div />
    </>
  )
}

export const Default = Template.bind({})
