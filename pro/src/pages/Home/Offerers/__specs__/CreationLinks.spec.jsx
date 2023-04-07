import {
  screen,
  waitForElementToBeRemoved,
  within,
} from '@testing-library/react'
import React from 'react'

import { api } from 'apiClient/api'
import * as useNewOfferCreationJourney from 'hooks/useNewOfferCreationJourney'
import { renderWithProviders } from 'utils/renderWithProviders'

import Homepage from '../../Homepage'

jest.mock('apiClient/api', () => ({
  api: {
    getOfferer: jest.fn(),
    listOfferersNames: jest.fn(),
    getVenueStats: jest.fn(),
  },
}))

jest.mock('hooks/useNewOfferCreationJourney', () => ({
  __esModule: true,
  default: jest.fn().mockReturnValue(false),
}))

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
        city: 'Cayenne',
        dateCreated: '2021-11-03T16:31:17.240807Z',
        dateModifiedAtLastProvider: '2021-11-03T16:31:18.294494Z',
        demarchesSimplifieesApplicationId: null,
        fieldsUpdated: [],
        hasDigitalVenueAtLeastOneOffer: true,
        id: 'GE',
        nonHumanizedId: 6,
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
        city: 'Drancy',
        dateCreated: '2021-11-03T16:31:17.240807Z',
        dateModifiedAtLastProvider: '2021-11-03T16:31:18.294494Z',
        demarchesSimplifieesApplicationId: null,
        fieldsUpdated: [],
        hasDigitalVenueAtLeastOneOffer: true,
        id: 'FQ',
        nonHumanizedId: 12,
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
  })

  describe('With new journey', () => {
    beforeEach(() => {
      jest.spyOn(useNewOfferCreationJourney, 'default').mockReturnValue(true)
    })
    it('Should not display creation links when user has no venue created', async () => {
      baseOfferers = [
        {
          ...baseOfferers[1],
          hasDigitalVenueAtLeastOneOffer: false,
          managedVenues: [],
        },
      ]
      api.getOfferer.mockResolvedValue(baseOfferers[0])
      await renderHomePage()
      expect(screen.queryByText('Ajouter un lieu')).not.toBeInTheDocument()
    })
    it('Should display creation links when user has a venue created', async () => {
      await renderHomePage()
      expect(screen.getByText('Ajouter un lieu')).toBeInTheDocument()
    })
  })

  describe('Without new journey', () => {
    beforeEach(() => {
      jest.spyOn(useNewOfferCreationJourney, 'default').mockReturnValue(false)
    })
    describe("when offerer doesn't have neither physical venue nor virtual offers", () => {
      it('should display add information link', async () => {
        // Given
        baseOfferers = [
          {
            ...baseOfferers[1],
            hasDigitalVenueAtLeastOneOffer: false,
            managedVenues: [virtualVenue],
          },
        ]
        api.getOfferer.mockResolvedValue(baseOfferers[0])
        await renderHomePage()

        // Then
        expect(
          screen.getByText(
            'Nous vous invitons à créer un lieu, cela vous permettra ensuite de créer des offres physiques ou des évènements qui seront réservables.'
          )
        ).toBeInTheDocument()

        expect(
          screen.getByRole('link', {
            name: 'Créer un lieu',
          })
        ).toBeInTheDocument()

        expect(
          screen.getByRole('link', {
            name: 'Créer une offre',
          })
        ).toBeInTheDocument()
      })
    })

    describe('when offerer have physical venue but no virtual offers', () => {
      it('sould display both creation links without card container', async () => {
        // Given
        baseOfferers = [
          {
            ...baseOfferers[0],
            hasDigitalVenueAtLeastOneOffer: false,
            managedVenues: [physicalVenue, virtualVenue],
          },
        ]
        api.getOfferer.mockResolvedValue(baseOfferers[0])
        await renderHomePage()

        // Then
        expect(
          screen.queryByText(
            'Nous vous invitons à créer un lieu, cela vous permettra ensuite de créer des offres physiques ou des évènements qui seront réservables.'
          )
        ).not.toBeInTheDocument()

        expect(
          screen.getByRole('link', {
            name: 'Créer une offre',
          })
        ).toBeInTheDocument()

        expect(
          screen.getByRole('link', {
            name: 'Ajouter un lieu',
          })
        ).toBeInTheDocument()
      })
    })

    describe("when offerer doesn't have physical venue but have virtual offers", () => {
      it('should only display "create venue" link without card container', async () => {
        // Given
        baseOfferers = [
          {
            ...baseOfferers[0],
            managedVenues: [virtualVenue],
          },
        ]
        api.getOfferer.mockResolvedValue(baseOfferers[0])
        await renderHomePage()

        // Then
        expect(
          screen.queryByText(
            'Nous vous invitons à créer un lieu, cela vous permettra ensuite de créer des offres physiques ou des évènements qui seront réservables.'
          )
        ).toBeInTheDocument()

        expect(
          screen.queryByRole('link', {
            name: 'Créer une offre',
          })
        ).toBeInTheDocument()

        expect(
          screen.getByRole('link', {
            name: 'Créer un lieu',
          })
        ).toBeInTheDocument()
      })
    })

    describe('when offerer have physical venue and virtual offers', () => {
      it('should only display "create venue" link without card container', async () => {
        // Given
        baseOfferers = [
          {
            ...baseOfferers[0],
            managedVenues: [physicalVenue, virtualVenue],
          },
        ]
        api.getOfferer.mockResolvedValue(baseOfferers[0])
        await renderHomePage()

        // Then
        expect(
          screen.queryByText(
            'Nous vous invitons à créer un lieu, cela vous permettra ensuite de créer des offres physiques ou des évènements qui seront réservables.'
          )
        ).not.toBeInTheDocument()
        expect(
          screen.queryByRole('link', {
            name: 'Créer une offre',
          })
        ).toBeInTheDocument()

        expect(
          screen.getByRole('link', {
            name: 'Ajouter un lieu',
          })
        ).toBeInTheDocument()
      })
    })

    describe('when user has no offerer', () => {
      beforeEach(async () => {
        api.listOfferersNames.mockResolvedValue({ offerersNames: [] })

        await renderHomePage()
      })

      it('should display offerer creation links', () => {
        expect(
          screen.getByText(
            'Votre précédente structure a été supprimée. Pour plus d’informations sur la suppression et vos données, veuillez contacter notre support.'
          )
        ).toBeInTheDocument()

        expect(
          screen.getByRole('link', { name: 'Ajouter une nouvelle structure' })
        ).toBeInTheDocument()

        const offererBanner = screen.getByTestId('offerers-creation-links-card')

        expect(
          within(offererBanner).getByRole('link', {
            name: 'Contacter le support',
          })
        ).toBeInTheDocument()
      })

      it('should not display venue creation links', () => {
        expect(
          screen.queryByText(
            'Nous vous invitons à créer un lieu, cela vous permettra ensuite de créer des offres physiques ou des évènements qui seront réservables.'
          )
        ).not.toBeInTheDocument()

        expect(
          screen.queryByRole('link', {
            name: 'Créer une offre',
          })
        ).not.toBeInTheDocument()

        expect(
          screen.queryByRole('link', {
            name: 'Ajouter un lieu',
          })
        ).not.toBeInTheDocument()
      })
    })
  })
})
