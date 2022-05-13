import React from 'react'
import { Router } from 'react-router-dom'
import { createBrowserHistory } from 'history'

type GetStory = () => React.ReactNode

export const withRouterDecorator = (getStory: GetStory): React.ReactNode => {
  const history = createBrowserHistory()
  return <Router history={history}>{getStory()}</Router>
}
