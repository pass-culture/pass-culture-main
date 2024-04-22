import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { renderWithProviders } from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

import { Welcome } from '..'

const renderWelcomeScreen = () => {
  return renderWithProviders(
    <Routes>
      <Route path="/parcours-inscription" element={<Welcome />} />
      <Route
        path="/parcours-inscription/structure"
        element={<div>Offerer screen</div>}
      />
    </Routes>,
    {
      user: sharedCurrentUserFactory(),
      initialRouterEntries: ['/parcours-inscription'],
    }
  )
}
describe('screens:SignupJourney::Welcome', () => {
  it('should render component', () => {
    renderWelcomeScreen()

    expect(screen.getByText('Finalisez votre inscription')).toBeInTheDocument()
  })

  it('should redirect user on offerer page on continue button click', async () => {
    renderWelcomeScreen()

    await userEvent.click(screen.getByText('Commencer'))

    expect(await screen.findByText('Offerer screen')).toBeInTheDocument()
  })
})
