import { createBrowserHistory } from 'history'
import React from 'react'
import { Router } from 'react-router-dom'

type GetStory = () => React.ReactNode

export const withRouterDecorator = (getStory: GetStory): React.ReactNode => {
  const history = createBrowserHistory()
  return <Router history={history}>{getStory()}</Router>
}
