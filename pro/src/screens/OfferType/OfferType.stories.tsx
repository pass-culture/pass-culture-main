import OfferType from './OfferType'
import React from 'react'
import { Router } from 'react-router-dom'
import { createBrowserHistory } from 'history'

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
