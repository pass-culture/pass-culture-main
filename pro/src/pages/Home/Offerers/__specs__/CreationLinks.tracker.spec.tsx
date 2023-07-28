import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { api } from 'apiClient/api'
import {
  GetOffererNameResponseModel,
  GetOffererResponseModel,
  GetOffererVenueResponseModel,
} from 'apiClient/v1'
import { Events } from 'core/FirebaseEvents/constants'
import * as useAnalytics from 'hooks/useAnalytics'
import { renderWithProviders } from 'utils/renderWithProviders'

import Homepage from '../../Homepage'

const mockLogEvent = vi.fn()
const renderHomePage = () => {
  const storeOverrides = {
    user: {
      currentUser: {
        id: 'fake_id',
        firstName: 'John',
        lastName: 'Do',
        email: 'john.do@dummy.xyz',
        phoneNumber: '01 00 00 00 00',
        hasSeenProTutorials: true,
      },
      initialized: true,
    },
  }

  renderWithProviders(<Homepage />, { storeOverrides })
}

describe('trackers creationLinks', () => {
  let baseOfferers: GetOffererResponseModel[]
  let baseOfferersNames: GetOffererNameResponseModel[]
  let virtualVenue: GetOffererVenueResponseModel
  let physicalVenue: GetOffererVenueResponseModel
  let physicalVenueWithPublicName

  beforeEach(() => {
    virtualVenue = {
      id: 1,
      isVirtual: true,
      name: 'Le Sous-sol (Offre numérique)',
      publicName: null,
    } as GetOffererVenueResponseModel

    physicalVenue = {
      id: 2,
      isVirtual: false,
      name: 'Le Sous-sol (Offre physique)',
      publicName: null,
    } as GetOffererVenueResponseModel

    physicalVenueWithPublicName = {
      id: 3,
      isVirtual: false,
      name: 'Le deuxième Sous-sol (Offre physique)',
      publicName: 'Le deuxième Sous-sol',
    } as GetOffererVenueResponseModel

    baseOfferers = [
      {
        address: 'LA COULÉE D’OR',
        apiKey: {
          maxAllowed: 5,
          prefixes: ['development_41'],
        },
        id: 6,
        city: 'Cayenne',
        dateCreated: '2021-11-03T16:31:17.240807Z',
        demarchesSimplifieesApplicationId: null,
        hasDigitalVenueAtLeastOneOffer: true,
        isValidated: true,
        isActive: true,
        name: 'Bar des amis',
        postalCode: '97300',
        siren: '111111111',
        managedVenues: [
          virtualVenue,
          physicalVenue,
          physicalVenueWithPublicName,
        ],
        hasAvailablePricingPoints: true,
      },
      {
        address: 'RUE DE NIEUPORT',
        apiKey: {
          maxAllowed: 5,
          prefixes: ['development_41'],
        },
        id: 12,
        city: 'Drancy',
        dateCreated: '2021-11-03T16:31:17.240807Z',
        demarchesSimplifieesApplicationId: null,
        hasDigitalVenueAtLeastOneOffer: true,
        isValidated: true,
        isActive: true,
        name: 'Club Dorothy',
        postalCode: '93700',
        siren: '222222222',
        managedVenues: [],
        hasAvailablePricingPoints: true,
      },
    ]
    baseOfferersNames = baseOfferers.map(offerer => ({
      id: offerer.id,
      name: offerer.name,
    }))

    vi.spyOn(api, 'getProfile')
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: baseOfferersNames,
    })
    vi.spyOn(api, 'getOfferer').mockResolvedValue(baseOfferers[0])
    vi.spyOn(api, 'getVenueStats').mockResolvedValue({
      activeBookingsQuantity: 4,
      activeOffersCount: 2,
      soldOutOffersCount: 3,
      validatedBookingsQuantity: 3,
    })
    vi.spyOn(api, 'postProFlags').mockResolvedValue()
    vi.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
  })

  it('should track venue creation link', async () => {
    // Given
    baseOfferers = [
      {
        ...baseOfferers[1],
        hasDigitalVenueAtLeastOneOffer: false,
      },
    ]
    vi.spyOn(api, 'getOfferer').mockResolvedValueOnce(baseOfferers[0])
    renderHomePage()
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    const createVenueButton = screen.getByText('Créer un lieu')

    await userEvent.click(createVenueButton)

    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_CREATE_VENUE,
      {
        from: '/',
        is_first_venue: true,
      }
    )
  })
})
