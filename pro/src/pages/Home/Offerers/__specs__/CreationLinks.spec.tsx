import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import React from 'react'

import { api } from 'apiClient/api'
import {
  GetOffererNameResponseModel,
  GetOffererResponseModel,
  GetOffererVenueResponseModel,
} from 'apiClient/v1'
import { renderWithProviders } from 'utils/renderWithProviders'

import Homepage from '../../Homepage'

const renderHomePage = async () => {
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

  await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))
}
describe('creationLinks', () => {
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
        city: 'Cayenne',
        dateCreated: '2021-11-03T16:31:17.240807Z',
        demarchesSimplifieesApplicationId: null,
        hasDigitalVenueAtLeastOneOffer: true,
        id: 6,
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
      } as GetOffererResponseModel,
      {
        address: 'RUE DE NIEUPORT',
        apiKey: {
          maxAllowed: 5,
          prefixes: ['development_41'],
        },
        city: 'Drancy',
        dateCreated: '2021-11-03T16:31:17.240807Z',
        demarchesSimplifieesApplicationId: null,
        hasDigitalVenueAtLeastOneOffer: true,
        id: 12,
        isValidated: true,
        isActive: true,
        name: 'Club Dorothy',
        postalCode: '93700',
        siren: '222222222',
        managedVenues: [],
        hasAvailablePricingPoints: true,
      } as GetOffererResponseModel,
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
  })

  it('Should not display creation links when user has no venue created', async () => {
    baseOfferers = [
      {
        ...baseOfferers[1],
        hasDigitalVenueAtLeastOneOffer: false,
        managedVenues: [],
      },
    ]
    vi.spyOn(api, 'getOfferer').mockResolvedValueOnce(baseOfferers[1])
    await renderHomePage()
    expect(screen.queryByText('Ajouter un lieu')).not.toBeInTheDocument()
  })

  it('Should display creation links when user has a venue created', async () => {
    await renderHomePage()
    expect(screen.getByText('Ajouter un lieu')).toBeInTheDocument()
  })
})
