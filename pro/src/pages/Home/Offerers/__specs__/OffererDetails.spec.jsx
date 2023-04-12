import {
  screen,
  waitForElementToBeRemoved,
  within,
} from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { api } from 'apiClient/api'
import * as useAnalytics from 'hooks/useAnalytics'
import * as useNewOfferCreationJourney from 'hooks/useNewOfferCreationJourney'
import { renderWithProviders } from 'utils/renderWithProviders'

import Homepage from '../../Homepage'

const mockNavigate = jest.fn()
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}))

jest.mock('apiClient/api', () => ({
  api: {
    getOfferer: jest.fn(),
    listOfferersNames: jest.fn(),
    getVenueStats: jest.fn(),
  },
}))

const renderHomePage = async storeOverrides => {
  const utils = renderWithProviders(<Homepage />, {
    storeOverrides,
  })

  await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

  const waitForElements = async () => {
    await screen.findByTestId('offerrer-wrapper')
    const offerer = screen.queryByTestId('offerrer-wrapper')
    const venues = screen.queryAllByTestId('venue-wrapper')

    const selectOfferer = async offererName => {
      await userEvent.selectOptions(
        within(offerer).getByRole('combobox'),
        offererName
      )
      const spinner = screen.queryByTestId('spinner')
      if (spinner) {
        await waitForElementToBeRemoved(spinner)
      }
    }

    return {
      offerer,
      venues,
      selectOfferer,
    }
  }

  return {
    ...utils,
    waitForElements,
  }
}
const mockLogEvent = jest.fn()

describe('offererDetailsLegacy', () => {
  let store
  let baseOfferers
  let firstOffererByAlphabeticalOrder
  let baseOfferersNames
  let virtualVenue
  let physicalVenue
  let physicalVenueWithPublicName

  beforeEach(() => {
    store = {
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

    virtualVenue = {
      id: 'test_venue_id_1',
      isVirtual: true,
      managingOffererId: 'GE',
      name: 'Le Sous-sol (Offre numérique)',
      offererName: 'Bar des amis',
      publicName: null,
      nOffers: 2,
    }
    physicalVenue = {
      id: 'test_venue_id_2',
      isVirtual: false,
      managingOffererId: 'GE',
      name: 'Le Sous-sol (Offre physique)',
      offererName: 'Bar des amis',
      publicName: null,
      nOffers: 2,
    }
    physicalVenueWithPublicName = {
      id: 'test_venue_id_3',
      isVirtual: false,
      managingOffererId: 'GE',
      name: 'Le deuxième Sous-sol (Offre physique)',
      offererName: 'Bar des amis',
      publicName: 'Le deuxième Sous-sol',
      nOffers: 2,
    }
    baseOfferers = [
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
        hasMissingBankInformation: true,
        id: 'FQ',
        nonHumanizedId: 6,
        isValidated: true,
        isActive: true,
        lastProviderId: null,
        name: 'Club Dorothy',
        postalCode: '93700',
        siren: '222222222',
        managedVenues: [
          {
            ...virtualVenue,
            id: 'test_venue_id_4',
            managingOffererId: 'FQ',
          },
        ],
      },
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
        hasMissingBankInformation: true,
        id: 'GE',
        nonHumanizedId: 12,
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
    ]
    firstOffererByAlphabeticalOrder = baseOfferers[1]
    baseOfferersNames = baseOfferers.map(offerer => ({
      id: offerer.id,
      name: offerer.name,
      nonHumanizedId: offerer.nonHumanizedId,
    }))

    api.listOfferersNames.mockResolvedValue({
      offerersNames: baseOfferersNames,
    })
    api.getOfferer.mockResolvedValue(firstOffererByAlphabeticalOrder)
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

  it('should display offerer select', async () => {
    const { waitForElements } = await renderHomePage(store)
    const { offerer } = await waitForElements()
    const showButton = within(offerer).getByRole('button', { name: 'Afficher' })
    await userEvent.click(showButton)

    expect(
      screen.getByDisplayValue(firstOffererByAlphabeticalOrder.name)
    ).toBeInTheDocument()
  })

  it('should not warn user when offerer is validated', async () => {
    // Given
    const { waitForElements } = await renderHomePage(store)
    const { offerer } = await waitForElements()
    const showButton = within(offerer).getByRole('button', { name: 'Afficher' })

    // When
    await userEvent.click(showButton)

    // Then
    expect(
      screen.queryByText(
        'Le rattachement à votre structure est en cours de traitement par les équipes du pass Culture'
      )
    ).not.toBeInTheDocument()
  })

  it('should display first offerer informations', async () => {
    const { waitForElements } = await renderHomePage(store)
    const { offerer } = await waitForElements()
    const showButton = within(offerer).getByRole('button', { name: 'Afficher' })
    await userEvent.click(showButton)

    const selectedOfferer = firstOffererByAlphabeticalOrder
    expect(screen.getByText(selectedOfferer.siren)).toBeInTheDocument()
    expect(
      screen.getByText(selectedOfferer.name, { selector: 'span' })
    ).toBeInTheDocument()
    expect(
      screen.getByText(selectedOfferer.address, { exact: false })
    ).toBeInTheDocument()
    expect(
      screen.getByText(
        `${selectedOfferer.postalCode} ${selectedOfferer.city}`,
        { exact: false }
      )
    ).toBeInTheDocument()
  })

  it('should display offerer venues informations', async () => {
    const { waitForElements } = await renderHomePage(store)
    const { offerer } = await waitForElements()
    const showButton = within(offerer).getByRole('button', { name: 'Afficher' })
    await userEvent.click(showButton)

    const selectedOfferer = firstOffererByAlphabeticalOrder
    const virtualVenueTitle = screen.getByText('Offres numériques')
    expect(virtualVenueTitle).toBeInTheDocument()

    const physicalVenueTitle = screen.getByText(
      selectedOfferer.managedVenues[1].name
    )
    expect(physicalVenueTitle).toBeInTheDocument()
    const physicalVenueContainer = physicalVenueTitle.closest('div')
    expect(
      within(physicalVenueContainer).getByText('Modifier', {
        exact: false,
      })
    ).toBeInTheDocument()

    const secondOfflineVenueTitle = screen.getByText(
      selectedOfferer.managedVenues[2].publicName
    )
    expect(secondOfflineVenueTitle).toBeInTheDocument()
  })

  it('should display edit venues with new offer creation journey', async () => {
    await jest
      .spyOn(useNewOfferCreationJourney, 'default')
      .mockReturnValue(true)
    await renderHomePage(store)

    const selectedOfferer = firstOffererByAlphabeticalOrder
    const physicalVenueTitle = screen.getByText(
      selectedOfferer.managedVenues[1].name
    )
    expect(physicalVenueTitle).toBeInTheDocument()
    const physicalVenueContainer = physicalVenueTitle.closest('div')
    expect(
      within(physicalVenueContainer).getByText('Éditer le lieu', {
        exact: false,
      })
    ).toBeInTheDocument()
  })

  it('should not display virtual venue informations when no virtual offers', async () => {
    // Given
    firstOffererByAlphabeticalOrder = {
      ...firstOffererByAlphabeticalOrder,
      hasDigitalVenueAtLeastOneOffer: false,
      managedVenues: [
        {
          ...virtualVenue,
        },
        physicalVenue,
      ],
    }
    api.getOfferer.mockResolvedValue(firstOffererByAlphabeticalOrder)

    // When
    const { waitForElements } = await renderHomePage(store)
    const { venues } = await waitForElements()

    // Then
    expect(venues).toHaveLength(1)
    expect(
      within(venues[0]).queryByText('Offre numérique')
    ).not.toBeInTheDocument()
  })

  describe('when user click on edit button', () => {
    it('should trigger an event when clicking on "Modifier" for offerers', async () => {
      const { waitForElements } = await renderHomePage(store)
      await waitForElements()

      const editButton = screen.getAllByText('Modifier', { exact: false })[0]
      await userEvent.click(editButton)

      expect(mockLogEvent).toHaveBeenCalledWith('hasClickedModifyOfferer', {
        offerer_id: 'GE',
      })
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
    })
  })

  describe('when selected offerer change', () => {
    let newSelectedOfferer
    beforeEach(async () => {
      newSelectedOfferer = {
        ...baseOfferers[0],
        managedVenues: [
          {
            id: 'test_venue_id_3',
            isVirtual: true,
            managingOffererId: baseOfferers[0].id,
            name: 'New venue (Offre numérique)',
            offererName: baseOfferers[0].name,
            publicName: null,
            nOffers: 2,
          },
          {
            id: 'test_venue_id_4',
            isVirtual: false,
            managingOffererId: baseOfferers[0].id,
            name: 'New venue (Offre physique)',
            offererName: baseOfferers[0].name,
            publicName: null,
            nOffers: 2,
          },
          {
            id: 'test_venue_id_5',
            isVirtual: false,
            managingOffererId: baseOfferers[0].id,
            name: 'Second new venue (Offre physique)',
            offererName: baseOfferers[0].name,
            publicName: 'Second new venue public name',
            nOffers: 2,
          },
        ],
      }
      api.getOfferer.mockResolvedValue(newSelectedOfferer)
      const { waitForElements } = await renderHomePage(store)
      const { selectOfferer } = await waitForElements()

      await selectOfferer(newSelectedOfferer.name)
      const newOfferer = screen.queryByTestId('offerrer-wrapper')

      const showButton = within(newOfferer).getByRole('button', {
        name: 'Afficher',
      })
      await userEvent.click(showButton)
    })

    it('should change displayed offerer informations', async () => {
      expect(
        await screen.findByText(newSelectedOfferer.siren)
      ).toBeInTheDocument()
      expect(
        screen.getByText(newSelectedOfferer.name, { selector: 'span' })
      ).toBeInTheDocument()
      expect(
        screen.getByText(newSelectedOfferer.address, { exact: false })
      ).toBeInTheDocument()
      expect(
        screen.getByText(
          `${newSelectedOfferer.postalCode} ${newSelectedOfferer.city}`,
          {
            exact: false,
          }
        )
      ).toBeInTheDocument()
    })

    it('should display new offerer venues informations', async () => {
      const virtualVenueTitle = screen.getByText('Offres numériques')
      expect(virtualVenueTitle).toBeInTheDocument()

      const physicalVenueTitle = await screen.findByText(
        newSelectedOfferer.managedVenues[1].name
      )
      expect(physicalVenueTitle).toBeInTheDocument()
      const physicalVenueContainer = physicalVenueTitle.closest('div')
      expect(
        within(physicalVenueContainer).getByText('Modifier', {
          exact: false,
        })
      ).toBeInTheDocument()

      const secondOfflineVenueTitle = screen.getByText(
        newSelectedOfferer.managedVenues[2].publicName
      )
      expect(secondOfflineVenueTitle).toBeInTheDocument()
    })
  })

  describe('when selecting "add offerer" option"', () => {
    it('should redirect to offerer creation page', async () => {
      // Given
      const { waitForElements } = await renderHomePage(store)
      const { selectOfferer } = await waitForElements()

      // When
      await selectOfferer('+ Ajouter une structure')

      // Then
      expect(mockNavigate).toHaveBeenCalledWith('/structures/creation')
    })
  })

  describe('when offerer has no physical venues', () => {
    let offererWithNoPhysicalVenues

    beforeEach(() => {
      const virtualVenue = {
        id: 'test_venue_id_1',
        isVirtual: true,
        managingOffererId: firstOffererByAlphabeticalOrder.id,
        name: 'Le Sous-sol (Offre numérique)',
        offererName: 'Bar des amis',
        publicName: null,
      }

      offererWithNoPhysicalVenues = {
        ...firstOffererByAlphabeticalOrder,
        managedVenues: [virtualVenue],
      }

      api.listOfferersNames.mockResolvedValue({
        offerersNames: [
          {
            id: offererWithNoPhysicalVenues.id,
            name: offererWithNoPhysicalVenues.name,
            nonHumanizedId: offererWithNoPhysicalVenues.nonHumanizedId,
          },
        ],
      })
      api.getOfferer.mockResolvedValue(offererWithNoPhysicalVenues)
    })

    it('should not display offerer informations', async () => {
      // When
      const { waitForElements } = await renderHomePage(store)
      const { offerer } = await waitForElements()

      // Then
      expect(
        within(offerer).queryByText(offererWithNoPhysicalVenues.siren)
      ).toBeInTheDocument()
      expect(
        within(offerer).queryByText(offererWithNoPhysicalVenues.name, {
          selector: 'span',
        })
      ).toBeInTheDocument()
      expect(
        within(offerer).queryByText(offererWithNoPhysicalVenues.address, {
          exact: false,
        })
      ).toBeInTheDocument()
      expect(
        within(offerer).queryByText(
          `${offererWithNoPhysicalVenues.postalCode} ${offererWithNoPhysicalVenues.city}`,
          { exact: false }
        )
      ).toBeInTheDocument()
    })

    it('should hide offerer informations on click on hide button', async () => {
      // Given
      const { waitForElements } = await renderHomePage(store)
      const { offerer } = await waitForElements()
      const hideButton = within(offerer).getByRole('button', {
        name: 'Masquer',
      })

      // When
      await userEvent.click(hideButton)

      //Then
      const selectedOffererAddress = `${offererWithNoPhysicalVenues.address} ${offererWithNoPhysicalVenues.postalCode} ${offererWithNoPhysicalVenues.city}`
      expect(
        within(offerer).queryByText(offererWithNoPhysicalVenues.siren)
      ).not.toBeInTheDocument()
      expect(
        within(offerer).queryByText(offererWithNoPhysicalVenues.name, {
          selector: 'span',
        })
      ).not.toBeInTheDocument()
      expect(
        within(offerer).queryByText(selectedOffererAddress)
      ).not.toBeInTheDocument()
    })
  })

  describe('when offerer has physical venues', () => {
    let offererWithPhysicalVenues

    beforeEach(() => {
      const offererVenues = [
        {
          id: 'test_venue_id_1',
          isVirtual: true,
          managingOffererId: firstOffererByAlphabeticalOrder.id,
          name: 'Le Sous-sol (Offre numérique)',
          offererName: 'Bar des amis',
          publicName: null,
        },
        {
          id: 'test_venue_id_2',
          isVirtual: false,
          managingOffererId: firstOffererByAlphabeticalOrder.id,
          name: 'Le Sous-sol (Offre physique)',
          offererName: 'Bar des amis',
          publicName: null,
        },
      ]
      offererWithPhysicalVenues = {
        ...firstOffererByAlphabeticalOrder,
        managedVenues: offererVenues,
      }

      api.listOfferersNames.mockResolvedValue({
        offerersNames: [
          {
            id: offererWithPhysicalVenues.id,
            name: offererWithPhysicalVenues.name,
            nonHumanizedId: offererWithPhysicalVenues.nonHumanizedId,
          },
        ],
      })
      api.getOfferer.mockResolvedValue(offererWithPhysicalVenues)
    })

    it('should not display offerer informations', async () => {
      // When
      const { waitForElements } = await renderHomePage(store)
      const { offerer } = await waitForElements()

      // Then
      const selectedOffererAddress = `${offererWithPhysicalVenues.address} ${offererWithPhysicalVenues.postalCode} ${offererWithPhysicalVenues.city}`
      expect(
        within(offerer).queryByText(offererWithPhysicalVenues.siren)
      ).not.toBeInTheDocument()
      expect(
        within(offerer).queryByText(offererWithPhysicalVenues.name, {
          selector: 'span',
        })
      ).not.toBeInTheDocument()
      expect(
        within(offerer).queryByText(selectedOffererAddress)
      ).not.toBeInTheDocument()
    })

    it('should show offerer informations on click on show button', async () => {
      // Given
      const { waitForElements } = await renderHomePage(store)
      const { offerer } = await waitForElements()
      const showButton = within(offerer).getByRole('button', {
        name: 'Afficher',
      })

      // When
      await userEvent.click(showButton)

      //Then
      expect(
        within(offerer).getByText(offererWithPhysicalVenues.siren)
      ).toBeInTheDocument()
      expect(
        within(offerer).getByText(offererWithPhysicalVenues.name, {
          selector: 'span',
        })
      ).toBeInTheDocument()
      expect(
        within(offerer).getByText(offererWithPhysicalVenues.address, {
          exact: false,
        })
      ).toBeInTheDocument()
      expect(
        within(offerer).getByText(
          `${offererWithPhysicalVenues.postalCode} ${offererWithPhysicalVenues.city}`,
          { exact: false }
        )
      ).toBeInTheDocument()
    })
  })

  describe('when offerer is not yet validated', () => {
    beforeEach(() => {
      virtualVenue = { ...virtualVenue, nOffers: 0 }
      const nonValidatedOfferer = {
        ...firstOffererByAlphabeticalOrder,
        isValidated: false,
        managedVenues: [virtualVenue],
      }
      api.listOfferersNames.mockResolvedValue({
        offerersNames: [
          {
            name: nonValidatedOfferer.name,
            id: nonValidatedOfferer.id,
            nonHumanizedId: nonValidatedOfferer.nonHumanizedId,
          },
        ],
      })
      api.getOfferer.mockResolvedValue(nonValidatedOfferer)
    })

    it('should warn user that offerer is being validated', async () => {
      // When
      const { waitForElements } = await renderHomePage(store)
      const { offerer } = await waitForElements()

      // Then
      expect(
        within(offerer).getByText(
          'Votre structure est en cours de traitement par les équipes du pass Culture'
        )
      ).toBeInTheDocument()
    })

    it('should allow user to view offerer informations', async () => {
      // When
      const { waitForElements } = await renderHomePage(store)
      const { offerer } = await waitForElements()

      // Then
      expect(
        within(offerer).queryByText('Informations pratiques')
      ).not.toBeInTheDocument()
    })

    it('should allow user to add venue and offer', async () => {
      // When
      const { waitForElements } = await renderHomePage(store)
      await waitForElements()

      // Then
      expect(
        screen.getByRole('link', { name: 'Créer un lieu' })
      ).toBeInTheDocument()
      expect(
        screen.getByRole('link', { name: 'Créer une offre' })
      ).toBeInTheDocument()
    })
  })

  describe('when user attachment to offerer is not yet validated', () => {
    beforeEach(() => {
      api.listOfferersNames.mockResolvedValue({
        offerersNames: [
          {
            name: firstOffererByAlphabeticalOrder.name,
            id: firstOffererByAlphabeticalOrder.id,
            nonHumanizedId: firstOffererByAlphabeticalOrder.nonHumanizedId,
          },
          {
            name: baseOfferers[0].name,
            id: baseOfferers[0].id,
            nonHumanizedId: baseOfferers[0].nonHumanizedId,
          },
        ],
      })
      api.getOfferer.mockRejectedValue({ status: 403 })
    })

    it('should warn user offerer is being validated', async () => {
      // When
      const { waitForElements } = await renderHomePage(store)
      await waitForElements()

      // Then
      expect(
        screen.queryByText(
          'Le rattachement à votre structure est en cours de traitement par les équipes du pass Culture'
        )
      ).toBeInTheDocument()
    })

    it('should not allow user to view offerer informations', async () => {
      // When
      const { waitForElements } = await renderHomePage(store)
      await waitForElements()
      // Then
      expect(
        screen.queryByText('Informations pratiques')
      ).not.toBeInTheDocument()
      expect(
        screen.queryByText('Coordonnées bancaires')
      ).not.toBeInTheDocument()
    })

    it('should not allow user to update offerer informations', async () => {
      // When
      const { waitForElements } = await renderHomePage(store)
      await waitForElements()

      // Then
      const [offererUpdateButton] = screen.getAllByRole('link', {
        name: 'Modifier',
      })
      expect(offererUpdateButton).toBeInTheDocument()
      expect(offererUpdateButton).toHaveAttribute('aria-disabled')
    })

    it('should not allow user to add venue and virtual offer', async () => {
      // When
      const { waitForElements } = await renderHomePage(store)
      await waitForElements()

      // Then
      expect(
        screen.queryByRole('link', { name: 'Créer un lieu' })
      ).not.toBeInTheDocument()
      expect(
        screen.queryByRole('link', { name: 'Créer une offre' })
      ).not.toBeInTheDocument()
    })

    it('should not show venues of previously selected offerer', async () => {
      // // Given
      api.getOfferer.mockResolvedValueOnce({
        ...firstOffererByAlphabeticalOrder,
        managedVenues: [virtualVenue, physicalVenue],
      })

      const { waitForElements } = await renderHomePage(store)
      await waitForElements()

      // When
      await userEvent.selectOptions(
        screen.getByDisplayValue(firstOffererByAlphabeticalOrder.name),
        firstOffererByAlphabeticalOrder.nonHumanizedId.toString()
      )

      // Then
      expect(api.getOfferer).toHaveBeenCalledTimes(1)

      const previouslySelectedOfferersPhysicalVenueName = screen.queryByRole(
        'heading',
        {
          level: 3,
          name: physicalVenue.name,
        }
      )
      expect(
        previouslySelectedOfferersPhysicalVenueName
      ).not.toBeInTheDocument()
    })
  })

  describe('when FF new bank informations creation', () => {
    beforeEach(() => {
      store = {
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
        app: { logEvent: mockLogEvent },
      }
    })

    it('should display missing bank information when at least one venue does not have a reimbursement point', async () => {
      firstOffererByAlphabeticalOrder = {
        ...firstOffererByAlphabeticalOrder,
        managedVenues: [
          {
            ...physicalVenue,
            hasMissingReimbursementPoint: true,
          },
          {
            ...physicalVenueWithPublicName,
            hasMissingReimbursementPoint: false,
          },
        ],
      }
      api.getOfferer.mockResolvedValue(firstOffererByAlphabeticalOrder)

      const { waitForElements } = await renderHomePage(store)
      const { offerer } = await waitForElements()

      expect(
        within(offerer).getByRole('button', {
          name: 'Masquer',
        })
      ).toBeInTheDocument()
      expect(
        within(offerer).getByText('Coordonnées bancaires')
      ).toBeInTheDocument()
    })

    it('should not display missing bank information when all venues has reimbursement point', async () => {
      firstOffererByAlphabeticalOrder = {
        ...firstOffererByAlphabeticalOrder,
        managedVenues: [
          {
            ...physicalVenue,
            hasMissingReimbursementPoint: false,
          },
          {
            ...physicalVenueWithPublicName,
            hasMissingReimbursementPoint: false,
          },
        ],
      }
      api.getOfferer.mockResolvedValue(firstOffererByAlphabeticalOrder)

      const { waitForElements } = await renderHomePage(store)
      const { offerer } = await waitForElements()

      const displayButton = within(offerer).getByRole('button', {
        name: 'Afficher',
      })
      expect(displayButton).toBeInTheDocument()

      // open offerer and wait that the block open.
      await userEvent.click(displayButton)
      expect(
        within(offerer).queryByText('Coordonnées bancaires')
      ).not.toBeInTheDocument()
    })
  })
})
