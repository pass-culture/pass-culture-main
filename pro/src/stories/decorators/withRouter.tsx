import React from 'react'
import { BrowserRouter } from 'react-router-dom'
import { CompatRouter } from 'react-router-dom-v5-compat'

type GetStory = () => React.ReactNode

export const withRouterDecorator = (getStory: GetStory): React.ReactNode => {
  return (
    <BrowserRouter>
      <CompatRouter>{getStory()}</CompatRouter>
    </BrowserRouter>
  )
}
