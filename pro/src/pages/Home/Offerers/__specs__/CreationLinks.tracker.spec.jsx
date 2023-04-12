import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { api } from 'apiClient/api'
import { Events } from 'core/FirebaseEvents/constants'
import * as useAnalytics from 'hooks/useAnalytics'
import { renderWithProviders } from 'utils/renderWithProviders'

import Homepage from '../../Homepage'

jest.mock('apiClient/api', () => ({
  api: {
    getOfferer: jest.fn().mockResolvedValue({}),
    listOfferersNames: jest.fn(),
    getVenueStats: jest.fn(),
  },
}))

const mockLogEvent = jest.fn()
const renderHomePage = () => {
  const storeOverrides = {
    user: {
      currentUser: {
        id: 'fake_id',
        firstName: 'John',
        lastName: 'Do',
        email: 'john.do@dummy.xyz',
        phoneNumber: '01 00 00 00 00',
      },
      initialized: true,
    },
  }

  renderWithProviders(<Homepage />, { storeOverrides })
}

describe('trackers creationLinks', () => {
  let baseOfferers
  let baseOfferersNames
  let virtualVenue
  let physicalVenue
  let physicalVenueWithPublicName

  beforeEach(() => {
    virtualVenue = {
      id: 'test_venue_id_1',
      isVirtual: true,
      managingOffererId: 'GE',
      name: 'Le Sous-sol (Offre numérique)',
      offererName: 'Bar des amis',
      publicName: null,
    }

    physicalVenue = {
      id: 'test_venue_id_2',
      isVirtual: false,
      managingOffererId: 'GE',
      name: 'Le Sous-sol (Offre physique)',
      offererName: 'Bar des amis',
      publicName: null,
    }

    physicalVenueWithPublicName = {
      id: 'test_venue_id_3',
      isVirtual: false,
      managingOffererId: 'GE',
      name: 'Le deuxième Sous-sol (Offre physique)',
      offererName: 'Bar des amis',
      publicName: 'Le deuxième Sous-sol',
    }

    baseOfferers = [
      {
        address: 'LA COULÉE D’OR',
        apiKey: {
          maxAllowed: 5,
          prefixes: ['development_41'],
        },
        nonHumanizedId: 6,
        city: 'Cayenne',
        dateCreated: '2021-11-03T16:31:17.240807Z',
        dateModifiedAtLastProvider: '2021-11-03T16:31:18.294494Z',
        demarchesSimplifieesApplicationId: null,
        fieldsUpdated: [],
        hasDigitalVenueAtLeastOneOffer: true,
        hasMissingBankInformation: false,
        id: 'GE',
        isValidated: true,
        isActive: true,
        lastProviderId: null,
        name: 'Bar des amis',
        postalCode: '97300',
        siren: '111111111',
        managedVenues: [
          virtualVenue,
          physicalVenue,
          physicalVenueWithPublicName,
        ],
      },
      {
        address: 'RUE DE NIEUPORT',
        apiKey: {
          maxAllowed: 5,
          prefixes: ['development_41'],
        },
        nonHumanizedId: 12,
        city: 'Drancy',
        dateCreated: '2021-11-03T16:31:17.240807Z',
        dateModifiedAtLastProvider: '2021-11-03T16:31:18.294494Z',
        demarchesSimplifieesApplicationId: null,
        fieldsUpdated: [],
        hasDigitalVenueAtLeastOneOffer: true,
        hasMissingBankInformation: false,
        id: 'FQ',
        isValidated: true,
        isActive: true,
        lastProviderId: null,
        name: 'Club Dorothy',
        postalCode: '93700',
        siren: '222222222',
        managedVenues: [],
      },
    ]
    baseOfferersNames = baseOfferers.map(offerer => ({
      id: offerer.id,
      name: offerer.name,
      nonHumanizedId: offerer.nonHumanizedId,
    }))

    api.getOfferer.mockResolvedValue(baseOfferers[0])
    api.listOfferersNames.mockResolvedValue({
      offerersNames: baseOfferersNames,
    })
    api.getVenueStats.mockResolvedValue({
      activeBookingsQuantity: 4,
      activeOffersCount: 2,
      soldOutOffersCount: 3,
      validatedBookingsQuantity: 3,
    })
    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
  })

  it('should track offer creation link', async () => {
    // Given
    baseOfferers = [
      {
        ...baseOfferers[1],
        hasDigitalVenueAtLeastOneOffer: false,
        managedVenues: [virtualVenue],
      },
    ]
    api.getOfferer.mockResolvedValue(baseOfferers[0])
    renderHomePage()
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    const createOfferButton = screen.queryByText('Créer une offre')

    await userEvent.click(createOfferButton)

    // Then
    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'Home',
        isEdition: false,
        to: 'OfferFormHomepage',
        used: 'HomeButton',
      }
    )
  })

  it('should track venue creation link', async () => {
    // Given
    baseOfferers = [
      {
        ...baseOfferers[1],
        hasDigitalVenueAtLeastOneOffer: false,
      },
    ]
    api.getOfferer.mockResolvedValue(baseOfferers[0])
    renderHomePage()
    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    const createVenueButton = screen.queryByText('Créer un lieu')

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
