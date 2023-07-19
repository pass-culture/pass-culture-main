import { screen } from '@testing-library/react'
import React from 'react'

import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { renderWithProviders } from 'utils/renderWithProviders'

import { BannerSummary } from '../'

describe('components:BannerSummary', () => {
  it('renders component successfully when offer is not draft', async () => {
    renderWithProviders(<BannerSummary mode={OFFER_WIZARD_MODE.CREATION} />)
    expect(
      screen.getByText(
        /Vérifiez les informations ci-dessous avant de publier votre offre./
      )
    ).toBeInTheDocument()
    expect(
      screen.getByText(
        /Si vous souhaitez la publier plus tard, vous pouvez retrouver votre brouillon dans la liste de vos offres./
      )
    ).toBeInTheDocument()
  })

  it('renders component successfully when offer is draft', async () => {
    renderWithProviders(<BannerSummary mode={OFFER_WIZARD_MODE.DRAFT} />)
    expect(
      screen.getByText(
        /Vérifiez les informations ci-dessous avant de publier votre offre./
      )
    ).toBeInTheDocument()
    expect(
      await screen.queryByText(
        /Si vous souhaitez la publier plus tard, vous pouvez retrouver votre brouillon dans la liste de vos offres./
      )
    ).not.toBeInTheDocument()
  })
})
