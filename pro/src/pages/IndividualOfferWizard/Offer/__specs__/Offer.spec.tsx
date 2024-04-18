import { screen } from '@testing-library/react'
import React from 'react'
import { generatePath } from 'react-router-dom'

import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { getIndividualOfferPath } from 'core/Offers/utils/getIndividualOfferUrl'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

import { Offer } from '../Offer'

const renderOfferPage = (options?: RenderWithProvidersOptions) =>
  renderWithProviders(<Offer />, options)

describe('Offer', () => {
  it('should display admin creation banner when no offererId is given', async () => {
    const url = generatePath(
      getIndividualOfferPath({
        step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
        mode: OFFER_WIZARD_MODE.CREATION,
        isCreation: true,
      })
    )

    renderOfferPage({
      user: sharedCurrentUserFactory({ isAdmin: true }),
      initialRouterEntries: [url],
    })

    expect(
      await screen.findByText(
        'Afin de créer une offre en tant qu’administrateur veuillez sélectionner une structure.'
      )
    ).toBeInTheDocument()
    expect(
      screen.queryByRole('heading', { name: 'Type d’offre' })
    ).not.toBeInTheDocument()
  })
})
