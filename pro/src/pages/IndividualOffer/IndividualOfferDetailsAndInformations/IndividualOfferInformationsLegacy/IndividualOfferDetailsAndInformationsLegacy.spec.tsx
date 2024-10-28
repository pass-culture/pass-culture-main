import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import React from 'react'
import { generatePath } from 'react-router-dom'

import { api } from 'apiClient/api'
import { OFFER_WIZARD_MODE } from 'commons/core/Offers/constants'
import { getIndividualOfferPath } from 'commons/core/Offers/utils/getIndividualOfferUrl'
import { venueListItemFactory } from 'commons/utils/individualApiFactories'
import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'commons/utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'commons/utils/storeFactories'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'

import { IndividualOfferDetailsAndInformationsLegacy } from './IndividualOfferDetailsAndInformationsLegacy'

const proVenues = [
  venueListItemFactory({
    id: 1,
    name: 'Ma venue',
    offererName: 'Mon offerer',
    publicName: undefined,
    isVirtual: false,
  }),
  venueListItemFactory({
    id: 2,
    name: 'Ma venue virtuelle',
    offererName: 'Mon offerer',
    isVirtual: true,
  }),
]

const renderOfferPage = (options?: RenderWithProvidersOptions) =>
  renderWithProviders(<IndividualOfferDetailsAndInformationsLegacy />, options)

describe('IndividualOfferDetailsAndInformationsLegacy', () => {
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

  it('should display offer', async () => {
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: [],
    })
    vi.spyOn(api, 'getVenues').mockResolvedValue({ venues: proVenues })

    renderOfferPage({
      user: sharedCurrentUserFactory(),
    })
    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(
      screen.getByRole('heading', { name: 'Type d’offre' })
    ).toBeInTheDocument()
  })
})
