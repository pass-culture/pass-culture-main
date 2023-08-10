import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import React from 'react'

import { api } from 'apiClient/api'
import { VenueTypeCode } from 'apiClient/v1'
import { HTTP_STATUS } from 'repository/pcapi/pcapiClient'
import { renderWithProviders } from 'utils/renderWithProviders'

import OffererDetails from '../OffererDetails'

vi.mock('react-router-dom', async () => ({
  ...((await vi.importActual('react-router-dom')) ?? {}),
  useParams: () => ({
    offererId: 'AA',
  }),
}))

describe('src | components | pages | Offerer | OffererDetails', () => {
  beforeEach(() => {
    const offererId = 1

    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      id: offererId,
      name: 'fake offerer name',
      city: 'Paris',
      postalCode: '75000',
      address: 'fake address',
      dateCreated: '2020-01-01T00:00:00.000Z',
      apiKey: {
        maxAllowed: 100,
        prefixes: [],
      },
      hasAvailablePricingPoints: true,
      hasDigitalVenueAtLeastOneOffer: true,
      isValidated: true,
      isActive: true,
      managedVenues: [
        {
          address: '1 fake address',
          name: 'fake venue',
          publicName: 'fake venue',
          postalCode: '75000',
          city: 'Paris',
          id: 1,
          collectiveDmsApplications: [],
          isVirtual: false,
          hasAdageId: false,
          hasCreatedOffer: false,
          hasMissingReimbursementPoint: false,
          venueTypeCode: VenueTypeCode.AUTRE,
        },
      ],
    })
  })

  describe('render', () => {
    it('should render Venues', async () => {
      renderWithProviders(<OffererDetails />)
      await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

      expect(screen.getByText('Lieux')).toBeInTheDocument()
      expect(screen.getByText('fake venue')).toBeInTheDocument()
    })

    it("shouldn't render anything if venues won't load", async () => {
      vi.spyOn(api, 'getOfferer').mockRejectedValueOnce({
        status: HTTP_STATUS.FORBIDDEN,
      })
      renderWithProviders(<OffererDetails />)
      await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

      expect(
        screen.queryByText(
          /Détails de la structure rattachée, des collaborateurs, des lieux et des fournisseurs de ses offres/
        )
      ).not.toBeInTheDocument()
    })

    it('Should show invite section if the FF is enabled', async () => {
      renderWithProviders(<OffererDetails />, {
        storeOverrides: {
          features: {
            list: [
              {
                nameKey: 'WIP_ENABLE_NEW_USER_OFFERER_LINK',
                isActive: true,
              },
            ],
            initialized: true,
          },
        },
      })
      await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

      expect(screen.getByText('Collaborateurs')).toBeInTheDocument()
    })
  })
})
