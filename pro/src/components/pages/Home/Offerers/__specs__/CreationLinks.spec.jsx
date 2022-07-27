import '@testing-library/jest-dom'

import { act, render, screen, within } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import * as pcapi from 'repository/pcapi/pcapi'
import { configureTestStore } from 'store/testUtils'

import Homepage from '../../Homepage'

jest.mock('repository/pcapi/pcapi', () => ({
  getOfferer: jest.fn(),
  getAllOfferersNames: jest.fn(),
  getVenueStats: jest.fn(),
}))

const renderHomePage = async () => {
  const store = configureTestStore({
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
  })

  return await act(async () => {
    await render(
      <Provider store={store}>
        <MemoryRouter>
          <Homepage />
        </MemoryRouter>
      </Provider>
    )
  })
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
        bic: 'test bic 01',
        city: 'Cayenne',
        dateCreated: '2021-11-03T16:31:17.240807Z',
        dateModifiedAtLastProvider: '2021-11-03T16:31:18.294494Z',
        demarchesSimplifieesApplicationId: null,
        fieldsUpdated: [],
        hasDigitalVenueAtLeastOneOffer: true,
        hasMissingBankInformation: false,
        iban: 'test iban 01',
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
        bic: 'test bic 02',
        city: 'Drancy',
        dateCreated: '2021-11-03T16:31:17.240807Z',
        dateModifiedAtLastProvider: '2021-11-03T16:31:18.294494Z',
        demarchesSimplifieesApplicationId: null,
        fieldsUpdated: [],
        hasDigitalVenueAtLeastOneOffer: true,
        hasMissingBankInformation: false,
        iban: 'test iban 02',
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
    }))

    pcapi.getOfferer.mockResolvedValue(baseOfferers[0])
    pcapi.getAllOfferersNames.mockResolvedValue(baseOfferersNames)
    pcapi.getVenueStats.mockResolvedValue({
      activeBookingsQuantity: 4,
      activeOffersCount: 2,
      soldOutOffersCount: 3,
      validatedBookingsQuantity: 3,
    })
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
      pcapi.getOfferer.mockResolvedValue(baseOfferers[0])
      await renderHomePage()

      // Then
      expect(
        screen.getByText(
          'Avant de créer votre première offre physique vous devez avoir un lieu'
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
      pcapi.getOfferer.mockResolvedValue(baseOfferers[0])
      await renderHomePage()

      // Then
      expect(
        screen.queryByText(
          'Avant de créer votre première offre physique vous devez avoir un lieu'
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
      pcapi.getOfferer.mockResolvedValue(baseOfferers[0])
      await renderHomePage()

      // Then
      expect(
        screen.queryByText(
          'Avant de créer votre première offre physique vous devez avoir un lieu'
        )
      ).not.toBeInTheDocument()

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
      pcapi.getOfferer.mockResolvedValue(baseOfferers[0])
      await renderHomePage()

      // Then
      expect(
        screen.queryByText(
          'Avant de créer votre première offre physique vous devez avoir un lieu'
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
      pcapi.getAllOfferersNames.mockResolvedValue([])

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
          'Avant de créer votre première offre physique vous devez avoir un lieu'
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
