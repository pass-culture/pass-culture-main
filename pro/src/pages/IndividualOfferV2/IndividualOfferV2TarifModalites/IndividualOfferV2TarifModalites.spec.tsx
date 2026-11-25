import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { IndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import {
  getIndividualOfferFactory,
  individualOfferContextValuesFactory,
} from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { Component as IndividualOfferV2TarifModalites } from './IndividualOfferV2TarifModalites'

const OFFER_ID = 12

const renderIndividualOfferV2TarifModalites = (isOnboarding = false) => {
  const baseUrl = isOnboarding ? '/onboarding' : ''

  return renderWithProviders(null, {
    storeOverrides: {
      user: {
        currentUser: sharedCurrentUserFactory(),
        selectedPartnerVenue: makeGetVenueResponseModel({ id: 1 }),
      },
    },
    initialRouterEntries: [
      `${baseUrl}/offre/individuelle/v2/${OFFER_ID}/creation/tarifs-modalites`,
    ],
    routes: [
      {
        path: `${baseUrl}/offre/individuelle/v2/:offerId/creation/tarifs-modalites`,
        element: (
          <IndividualOfferContext.Provider
            value={individualOfferContextValuesFactory({
              offer: getIndividualOfferFactory({ id: OFFER_ID }),
            })}
          >
            <IndividualOfferV2TarifModalites />
          </IndividualOfferContext.Provider>
        ),
      },
      {
        path: `${baseUrl}/offre/individuelle/v2/:offerId/creation/description`,
        element: <h2>Description</h2>,
      },
    ],
  })
}

describe('<IndividualOfferV2TarifModalites />', () => {
  it('should have no accessibility violations', async () => {
    const { container } = renderIndividualOfferV2TarifModalites()

    expect(await axe(container)).toHaveNoViolations()
  })

  it.each([
    { isOnboarding: false, baseUrl: '' },
    { isOnboarding: true, baseUrl: '/onboarding' },
  ])(
    'should navigate to the description step when clicking on previous step (onboarding: $isOnboarding)',
    async ({ isOnboarding, baseUrl }) => {
      const user = userEvent.setup()
      const { router } = renderIndividualOfferV2TarifModalites(isOnboarding)

      await user.click(screen.getByRole('button', { name: 'Étape précédente' }))

      expect(router.state.location.pathname).toBe(
        `${baseUrl}/offre/individuelle/v2/${OFFER_ID}/creation/description`
      )
      expect(
        screen.getByRole('heading', { name: 'Description' })
      ).toBeInTheDocument()
    }
  )
})
