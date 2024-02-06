import { screen } from '@testing-library/react'

import { AdageUserContextProvider } from 'pages/AdageIframe/app/providers/AdageUserContext'
import {
  defaultAdageUser,
  defaultCollectiveTemplateOffer,
} from 'utils/adageFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import AdageOffer from '../AdageOffer'

describe('AdageOffer', () => {
  it('should display the offer information sections', () => {
    renderWithProviders(
      <AdageUserContextProvider adageUser={defaultAdageUser}>
        <AdageOffer offer={defaultCollectiveTemplateOffer} />
      </AdageUserContextProvider>
    )

    expect(
      screen.getByRole('heading', { name: 'Détails de l’offre' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('heading', { name: 'Informations pratiques' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('heading', { name: 'Public concerné' })
    ).toBeInTheDocument()
  })
})
