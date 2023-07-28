import {
  screen,
  waitForElementToBeRemoved,
  within,
} from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { api } from 'apiClient/api'
import {
  GetOffererNameResponseModel,
  GetOffererResponseModel,
  GetOffererVenueResponseModel,
} from 'apiClient/v1'
import * as useAnalytics from 'hooks/useAnalytics'
import { renderWithProviders } from 'utils/renderWithProviders'

import Homepage from '../../Homepage'

const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => ({
  ...((await vi.importActual('react-router-dom')) as object),
  useNavigate: () => mockNavigate,
}))

const renderHomePage = async (storeOverrides: any) => {
  const utils = renderWithProviders(<Homepage />, {
    storeOverrides,
  })

  await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

  const waitForElements = async () => {
    await screen.findByTestId('offerrer-wrapper')
    const offerer = screen.getByTestId('offerrer-wrapper')
    const venues = screen.queryAllByTestId('venue-wrapper')

    const selectOfferer = async (offererName: string) => {
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
const mockLogEvent = vi.fn()

describe('offererDetailsLegacy', () => {
  let store: any
  let baseOfferers: GetOffererResponseModel[]
  let firstOffererByAlphabeticalOrder: GetOffererResponseModel
  let baseOfferersNames: GetOffererNameResponseModel[]
  let virtualVenue: GetOffererVenueResponseModel
  let physicalVenue: GetOffererVenueResponseModel
  let physicalVenueWithPublicName: GetOffererVenueResponseModel

  beforeEach(() => {
    store = {
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
        address: 'RUE DE NIEUPORT',
        apiKey: {
          maxAllowed: 5,
          prefixes: ['development_41'],
        },
        city: 'Drancy',
        dateCreated: '2021-11-03T16:31:17.240807Z',
        demarchesSimplifieesApplicationId: null,
        hasDigitalVenueAtLeastOneOffer: true,
        id: 6,
        isValidated: true,
        isActive: true,
        name: 'Club Dorothy',
        postalCode: '93700',
        siren: '222222222',
        managedVenues: [
          {
            ...virtualVenue,
            id: 4,
          },
        ],
        hasAvailablePricingPoints: true,
      },
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
        id: 12,
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
    ]
    firstOffererByAlphabeticalOrder = baseOfferers[1]
    baseOfferersNames = baseOfferers.map(offerer => ({
      id: offerer.id,
      name: offerer.name,
    }))

    vi.spyOn(api, 'getProfile')
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: baseOfferersNames,
    })
    vi.spyOn(api, 'getOfferer').mockResolvedValue(
      firstOffererByAlphabeticalOrder
    )
    vi.spyOn(api, 'getVenueStats').mockResolvedValue({
      activeBookingsQuantity: 4,
      activeOffersCount: 2,
      soldOutOffersCount: 3,
      validatedBookingsQuantity: 3,
    })
    vi.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
  })

  it('should display offerer select', async () => {
    await renderHomePage(store)

    expect(
      screen.getByText(firstOffererByAlphabeticalOrder.name)
    ).toBeInTheDocument()
  })

  it('should not warn user when offerer is validated', async () => {
    // Given
    await renderHomePage(store)

    // Then
    expect(
      screen.queryByText(
        'Le rattachement à votre structure est en cours de traitement par les équipes du pass Culture'
      )
    ).not.toBeInTheDocument()
  })

  it('should display offerer venues informations', async () => {
    await renderHomePage(store)

    const virtualVenueTitle = screen.getByText('Offres numériques')
    expect(virtualVenueTitle).toBeInTheDocument()
    const physicalVenueTitle = screen.getByText(physicalVenue.name)
    expect(physicalVenueTitle).toBeInTheDocument()
    const physicalVenueContainer = physicalVenueTitle.closest('div')
    expect(
      physicalVenueContainer &&
        within(physicalVenueContainer).getByText('Éditer le lieu', {
          exact: false,
        })
    ).toBeInTheDocument()

    const secondOfflineVenueTitle = screen.getByText('Le deuxième Sous-sol')
    expect(secondOfflineVenueTitle).toBeInTheDocument()
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
    vi.spyOn(api, 'getOfferer').mockResolvedValueOnce(
      firstOffererByAlphabeticalOrder
    )

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
        offerer_id: 12,
      })
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
    })
  })

  describe('when selected offerer change', () => {
    let newSelectedOfferer: GetOffererResponseModel
    beforeEach(async () => {
      newSelectedOfferer = {
        ...baseOfferers[0],
        managedVenues: [
          {
            id: 1,
            isVirtual: true,
            name: 'New venue (Offre numérique)',
            publicName: null,
          } as GetOffererVenueResponseModel,
          {
            id: 2,
            isVirtual: false,
            name: 'New venue (Offre physique)',
            publicName: null,
          } as GetOffererVenueResponseModel,
          {
            id: 3,
            isVirtual: false,
            name: 'Second new venue (Offre physique)',
            publicName: 'Second new venue public name',
          } as GetOffererVenueResponseModel,
        ],
      }
      vi.spyOn(api, 'getOfferer').mockResolvedValueOnce(newSelectedOfferer)
      const { waitForElements } = await renderHomePage(store)
      const { selectOfferer } = await waitForElements()

      await selectOfferer(newSelectedOfferer.name)
    })

    it('should display new offerer venues informations', async () => {
      const virtualVenueTitle = screen.getByText('Offres numériques')
      expect(virtualVenueTitle).toBeInTheDocument()

      const physicalVenueTitle =
        newSelectedOfferer.managedVenues &&
        (await screen.findByText(newSelectedOfferer.managedVenues[1].name))
      expect(physicalVenueTitle).toBeInTheDocument()
      const physicalVenueContainer =
        physicalVenueTitle && physicalVenueTitle.closest('div')

      expect(
        physicalVenueContainer &&
          within(physicalVenueContainer).getByText('Éditer le lieu', {
            exact: false,
          })
      ).toBeInTheDocument()
      const secondOfflineVenueTitle = screen.getByText(
        'Second new venue public name'
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

  describe('when offerer has physical venues', () => {
    let offererWithPhysicalVenues: GetOffererResponseModel

    beforeEach(() => {
      const offererVenues = [
        {
          id: 1,
          isVirtual: true,
          name: 'Le Sous-sol (Offre numérique)',
          publicName: null,
        } as GetOffererVenueResponseModel,
        {
          id: 2,
          isVirtual: false,
          name: 'Le Sous-sol (Offre physique)',
          publicName: null,
        } as GetOffererVenueResponseModel,
      ]
      offererWithPhysicalVenues = {
        ...firstOffererByAlphabeticalOrder,
        managedVenues: offererVenues,
      }

      vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
        offerersNames: [
          {
            id: offererWithPhysicalVenues.id,
            name: offererWithPhysicalVenues.name,
          },
        ],
      })
      vi.spyOn(api, 'getOfferer').mockResolvedValue(offererWithPhysicalVenues)
    })

    it('should not display offerer informations', async () => {
      // When
      const { waitForElements } = await renderHomePage(store)
      const { offerer } = await waitForElements()

      // Then
      const selectedOffererAddress = `${offererWithPhysicalVenues.address} ${offererWithPhysicalVenues.postalCode} ${offererWithPhysicalVenues.city}`
      expect(within(offerer).queryByText('111111111')).not.toBeInTheDocument()
      expect(
        within(offerer).queryByText(offererWithPhysicalVenues.name, {
          selector: 'span',
        })
      ).not.toBeInTheDocument()
      expect(
        within(offerer).queryByText(selectedOffererAddress)
      ).not.toBeInTheDocument()
    })
  })

  describe('when offerer is not yet validated', () => {
    beforeEach(() => {
      virtualVenue = { ...virtualVenue }
      const nonValidatedOfferer = {
        ...firstOffererByAlphabeticalOrder,
        isValidated: false,
        managedVenues: [virtualVenue],
      }
      vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
        offerersNames: [
          {
            name: nonValidatedOfferer.name,
            id: nonValidatedOfferer.id,
          },
        ],
      })
      vi.spyOn(api, 'getOfferer').mockResolvedValue(nonValidatedOfferer)
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
  })

  describe('when user attachment to offerer is not yet validated', () => {
    beforeEach(() => {
      vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
        offerersNames: [
          {
            name: firstOffererByAlphabeticalOrder.name,
            id: firstOffererByAlphabeticalOrder.id,
          },
          {
            name: baseOfferers[0].name,
            id: baseOfferers[0].id,
          },
        ],
      })
      vi.spyOn(api, 'getOfferer').mockRejectedValue({ status: 403 })
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
      // Given
      vi.spyOn(api, 'getOfferer').mockResolvedValueOnce({
        ...firstOffererByAlphabeticalOrder,
        managedVenues: [virtualVenue, physicalVenue],
      })

      const { waitForElements } = await renderHomePage(store)
      await waitForElements()

      // When
      await userEvent.selectOptions(
        screen.getByDisplayValue(firstOffererByAlphabeticalOrder.name),
        firstOffererByAlphabeticalOrder.id.toString()
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
})
