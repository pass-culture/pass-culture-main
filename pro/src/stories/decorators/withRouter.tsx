import React from 'react'
import { BrowserRouter } from 'react-router-dom-v5-compat'

type GetStory = () => React.ReactNode

export const withRouterDecorator = (getStory: GetStory): React.ReactNode => (
  <BrowserRouter>{getStory()}</BrowserRouter>
)
