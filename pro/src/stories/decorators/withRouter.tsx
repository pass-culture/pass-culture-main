import React from 'react'
import { BrowserRouter } from 'react-router-dom'

type GetStory = () => React.ReactNode

export const withRouterDecorator = (getStory: GetStory): React.ReactNode => (
  <BrowserRouter>{getStory()}</BrowserRouter>
)
