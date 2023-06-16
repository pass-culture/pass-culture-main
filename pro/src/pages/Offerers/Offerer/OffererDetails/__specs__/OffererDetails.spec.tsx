import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import React from 'react'

import { api } from 'apiClient/api'
import { VenueTypeCode } from 'apiClient/v1'
import { renderWithProviders } from 'utils/renderWithProviders'

import OffererDetails from '../OffererDetails'

jest.mock('apiClient/api', () => ({
  api: {
    getOfferer: jest.fn(),
  },
}))

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: () => ({
    offererId: 'AA',
  }),
}))

describe('src | components | pages | Offerer | OffererDetails', () => {
  const offererId = 1

  jest.spyOn(api, 'getOfferer').mockResolvedValue({
    nonHumanizedId: offererId,
    name: 'fake offerer name',
    city: 'Paris',
    postalCode: '75000',
    address: 'fake address',
    dateCreated: '2020-01-01T00:00:00.000Z',
    fieldsUpdated: ['postalCode', 'city'],
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
        id: 'AA',
        nonHumanizedId: 1,
        collectiveDmsApplications: [],
        isVirtual: false,
        hasAdageId: false,
        hasCreatedOffer: false,
        hasMissingReimbursementPoint: false,
        venueTypeCode: VenueTypeCode.AUTRE,
        managingOffererId: 'AA',
      },
    ],
  })

  describe('render', () => {
    it('should render Venues', async () => {
      renderWithProviders(<OffererDetails />)
      await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

      expect(screen.getByText('Lieux')).toBeInTheDocument()
      expect(screen.getByText('fake venue')).toBeInTheDocument()
    })
  })
})
