import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Route, Routes } from 'react-router'

import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { ConfirmedAttachment } from '../ConfirmedAttachment'

const renderConfirmedAttachmentScreen = () => {
  return renderWithProviders(
    <Routes>
      <Route
        path="/inscription/structure/rattachement/confirmation"
        element={<ConfirmedAttachment />}
      />
      <Route path="/accueil" element={<div>Home screen</div>} />
    </Routes>,
    {
      user: sharedCurrentUserFactory(),
      initialRouterEntries: [
        '/inscription/structure/rattachement/confirmation',
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
