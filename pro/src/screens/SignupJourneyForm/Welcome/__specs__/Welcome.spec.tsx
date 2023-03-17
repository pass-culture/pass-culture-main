import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Route, Routes } from 'react-router-dom-v5-compat'

import { renderWithProviders } from 'utils/renderWithProviders'

import { Welcome } from '..'

const renderWelcomeScreen = () => {
  const storeOverrides = {
    user: {
      initialized: true,
      currentUser: {
        publicName: 'John Do',
        isAdmin: false,
        email: 'email@example.com',
      },
    },
  }

  return renderWithProviders(
    <Routes>
      <Route path="/parcours-inscription" element={<Welcome />} />
      <Route
        path="/parcours-inscription/structure"
        element={<div>Offerer screen</div>}
      />
    </Routes>,
    {
      storeOverrides,
      initialRouterEntries: ['/parcours-inscription'],
    }
  )
}
describe('screens:SignupJourney::Welcome', () => {
  it('should render component', async () => {
    renderWelcomeScreen()

    expect(
      await screen.getByText('Finalisez votre inscription')
    ).toBeInTheDocument()
  })

  it('should redirect user on offerer page on continue button click', async () => {
    renderWelcomeScreen()

    await userEvent.click(screen.getByText('Commencer'))

    expect(await screen.findByText('Offerer screen')).toBeInTheDocument()
  })
})
