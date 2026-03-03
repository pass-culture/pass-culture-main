import { screen } from '@testing-library/react'
import { Route, Routes } from 'react-router'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { SubscriptionRedirection } from './SubscriptionRedirection'

const render = (features: string[] = []) => {
  return renderWithProviders(
    <Routes>
      <Route path="/inscription" element={<SubscriptionRedirection />}></Route>
      <Route path="/bienvenue" element={<span>Bienvenue</span>}></Route>
      <Route
        path="/inscription/compte/creation"
        element={<span>Inscription</span>}
      ></Route>
    </Routes>,
    {
      initialRouterEntries: ['/inscription'],
      features,
    }
  )
}

describe('<SubscriptionRedirection />', () => {
  it('should redirect to welcome page  if WIP_PRE_SIGNUP_INFO is enabled', () => {
    render(['WIP_PRE_SIGNUP_INFO'])
    expect(screen.getByText('Bienvenue')).toBeInTheDocument()
  })
  it('should redirect to subscription page  if WIP_PRE_SIGNUP_INFO is disabled', () => {
    render([])
    expect(screen.getByText('Inscription')).toBeInTheDocument()
  })
})
