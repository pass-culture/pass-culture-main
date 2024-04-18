import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { renderWithProviders } from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

import { ConfirmedAttachment } from '..'

const renderConfirmedAttachmentScreen = () => {
  return renderWithProviders(
    <Routes>
      <Route
        path="/parcours-inscription/structure/rattachement/confirmation"
        element={<ConfirmedAttachment />}
      />
      <Route path="/accueil" element={<div>Home screen</div>} />
    </Routes>,
    {
      user: sharedCurrentUserFactory(),
      initialRouterEntries: [
        '/parcours-inscription/structure/rattachement/confirmation',
      ],
    }
  )
}
describe('screens:SignupJourney::ConfirmedAttachment', () => {
  it('should render component', () => {
    renderConfirmedAttachmentScreen()

    expect(
      screen.getByText('Votre demande a été prise en compte')
    ).toBeInTheDocument()
  })

  it('should redirect user on offerer page on continue button click', async () => {
    renderConfirmedAttachmentScreen()

    await userEvent.click(screen.getByText('Accéder à votre espace'))

    expect(await screen.findByText('Home screen')).toBeInTheDocument()
  })
})
