import '@testing-library/jest-dom'

import {
  fireEvent,
  render,
  screen,
  waitForElementToBeRemoved,
  within,
} from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import * as useAnalytics from 'components/hooks/useAnalytics'
import { Events } from 'core/FirebaseEvents/constants'
import * as pcapi from 'repository/pcapi/pcapi'
import { configureTestStore } from 'store/testUtils'

import Homepage from '../../Homepage'

const mockHistoryPush = jest.fn()
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useHistory: () => ({
    push: mockHistoryPush,
  }),
}))

jest.mock('utils/config', () => ({
  DEMARCHES_SIMPLIFIEES_BUSINESS_UNIT_RIB_UPLOAD_PROCEDURE_URL:
    'link/to/businesUnit/demarchesSimplifiees/procedure',
}))

jest.mock('repository/pcapi/pcapi', () => ({
  getOfferer: jest.fn(),
  getAllOfferersNames: jest.fn(),
  getVenueStats: jest.fn(),
  getBusinessUnits: jest.fn(),
}))

const renderHomePage = ({ store }) => {
  const utils = render(
    <Provider store={store}>
      <MemoryRouter>
        <Homepage />
      </MemoryRouter>
    </Provider>
  )

  const waitForElements = async () => {
    await screen.findByTestId('offerrer-wrapper')
    const offerer = screen.queryByTestId('offerrer-wrapper')
    const venues = screen.queryAllByTestId('venue-wrapper')

    const selectOfferer = async offererName => {
      await userEvent.selectOptions(
        within(offerer).getByDisplayValue('Bar des amis'),
        offererName
      )
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
    store = configureTestStore({
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
        bic: 'test bic 02',
        city: 'Drancy',
        dateCreated: '2021-11-03T16:31:17.240807Z',
        dateModifiedAtLastProvider: '2021-11-03T16:31:18.294494Z',
        demarchesSimplifieesApplicationId: null,
        fieldsUpdated: [],
        hasDigitalVenueAtLeastOneOffer: true,
        hasMissingBankInformation: true,
        iban: 'test iban 02',
        id: 'FQ',
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
        bic: 'test bic 01',
        city: 'Cayenne',
        dateCreated: '2021-11-03T16:31:17.240807Z',
        dateModifiedAtLastProvider: '2021-11-03T16:31:18.294494Z',
        demarchesSimplifieesApplicationId: null,
        fieldsUpdated: [],
        hasDigitalVenueAtLeastOneOffer: true,
        hasMissingBankInformation: true,
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
    ]
    firstOffererByAlphabeticalOrder = baseOfferers[1]
    baseOfferersNames = baseOfferers.map(offerer => ({
      id: offerer.id,
      name: offerer.name,
    }))

    pcapi.getOfferer.mockResolvedValue(firstOffererByAlphabeticalOrder)
    pcapi.getAllOfferersNames.mockResolvedValue(baseOfferersNames)
    pcapi.getVenueStats.mockResolvedValue({
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
    const { waitForElements } = renderHomePage({ store })
    const { offerer } = await waitForElements()
    const showButton = within(offerer).getByRole('button', { name: 'Afficher' })
    fireEvent.click(showButton)

    expect(
      screen.getByDisplayValue(firstOffererByAlphabeticalOrder.name)
    ).toBeInTheDocument()
  })

  it('should not warn user when offerer is validated', async () => {
    // Given
    const { waitForElements } = renderHomePage({ store })
    const { offerer } = await waitForElements()
    const showButton = within(offerer).getByRole('button', { name: 'Afficher' })

    // When
    fireEvent.click(showButton)

    // Then
    expect(
      screen.queryByText('Votre structure est en cours de validation')
    ).not.toBeInTheDocument()
  })

  it('should display first offerer informations', async () => {
    const { waitForElements } = renderHomePage({ store })
    const { offerer } = await waitForElements()
    const showButton = within(offerer).getByRole('button', { name: 'Afficher' })
    fireEvent.click(showButton)

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
    const { waitForElements } = renderHomePage({ store })
    const { offerer } = await waitForElements()
    const showButton = within(offerer).getByRole('button', { name: 'Afficher' })
    fireEvent.click(showButton)

    const selectedOfferer = firstOffererByAlphabeticalOrder
    const virtualVenueTitle = screen.getByText('Offres numériques')
    expect(virtualVenueTitle).toBeInTheDocument()

    const physicalVenueTitle = screen.getByText(
      selectedOfferer.managedVenues[1].name
    )
    expect(physicalVenueTitle).toBeInTheDocument()
    const physicalVenueContainer = physicalVenueTitle.closest('div')
    expect(
      within(physicalVenueContainer).getByText('Modifier', { exact: false })
    ).toBeInTheDocument()

    const secondOfflineVenueTitle = screen.getByText(
      selectedOfferer.managedVenues[2].publicName
    )
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
    pcapi.getOfferer.mockResolvedValue(firstOffererByAlphabeticalOrder)

    // When
    const { waitForElements } = renderHomePage({ store })
    const { venues } = await waitForElements()

    // Then
    expect(venues).toHaveLength(1)
    expect(
      within(venues[0]).queryByText('Offre numérique')
    ).not.toBeInTheDocument()
  })

  describe('when user click on edit button', () => {
    it('should trigger an event when clicking on "Modifier" for offerers', async () => {
      const { waitForElements } = await renderHomePage({ store })
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
      const { waitForElements } = renderHomePage({ store })
      const { selectOfferer } = await waitForElements()
      pcapi.getOfferer.mockResolvedValue(newSelectedOfferer)

      selectOfferer(newSelectedOfferer.name)
      const { offerer: newOfferer } = await waitForElements()

      const showButton = within(newOfferer).getByRole('button', {
        name: 'Afficher',
      })
      fireEvent.click(showButton)
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
        within(physicalVenueContainer).getByText('Modifier', { exact: false })
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
      const { waitForElements } = renderHomePage({ store })
      const { selectOfferer } = await waitForElements()
      // When
      await selectOfferer('+ Ajouter une structure')

      // Then
      expect(mockHistoryPush).toHaveBeenCalledWith('/structures/creation')
    })
  })

  describe("when offerer doesn't have bank informations", () => {
    it('should display bank warning if offerer has missing bank information', async () => {
      // Given
      pcapi.getOfferer.mockResolvedValue(firstOffererByAlphabeticalOrder)

      // When
      const { waitForElements } = renderHomePage({ store })
      const { offerer } = await waitForElements()
      const showButton = within(offerer).getByRole('button', {
        name: 'Afficher',
      })
      await userEvent.click(showButton)

      // Then
      const link = screen.getByRole('link', {
        name: 'Renseigner des coordonnées bancaires',
      })
      expect(link).toBeInTheDocument()
      const warningIcons = screen.getAllByAltText(
        'Informations bancaires manquantes'
      )
      let nbWarningIcons = 0
      nbWarningIcons += 1 // in offerers header
      expect(warningIcons).toHaveLength(nbWarningIcons)
    })

    it("shouldn't display bank warning offerer has NO missing bank information", async () => {
      pcapi.getOfferer.mockResolvedValue({
        ...firstOffererByAlphabeticalOrder,
        hasMissingBankInformation: false,
      })
      const { waitForElements } = renderHomePage({ store })
      const { offerer } = await waitForElements()
      const warningIcons = within(offerer).queryByAltText(
        'Informations bancaires manquantes'
      )
      expect(warningIcons).not.toBeInTheDocument()
    })

    it('should display file information for pending registration', async () => {
      baseOfferers = [
        {
          ...firstOffererByAlphabeticalOrder,
          hasMissingBankInformation: false,
          bic: '',
          iban: '',
          demarchesSimplifieesApplicationId:
            'demarchesSimplifieesApplication_fake_id',
        },
      ]
      pcapi.getOfferer.mockResolvedValue(baseOfferers[0])
      const { waitForElements } = renderHomePage({ store })
      const { offerer } = await waitForElements()
      const showButton = within(offerer).getByRole('button', {
        name: 'Afficher',
      })
      fireEvent.click(showButton)
      expect(
        screen.getByRole('link', { name: 'Voir le dossier' })
      ).toBeInTheDocument()
      const warningIcons = within(offerer).queryByAltText(
        'Informations bancaires manquantes'
      )
      expect(warningIcons).not.toBeInTheDocument()
    })
  })

  describe('when offerer has no physical venues', () => {
    let offererWithNoPhysicalVenues

    beforeEach(() => {
      const virtualVenue = {
        id: 'test_venue_id_1',
        isValidated: true,
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

      pcapi.getOfferer.mockResolvedValue(offererWithNoPhysicalVenues)
      pcapi.getAllOfferersNames.mockResolvedValue([
        {
          id: offererWithNoPhysicalVenues.id,
          name: offererWithNoPhysicalVenues.name,
        },
      ])
    })

    it('should display offerer informations', async () => {
      // When
      const { waitForElements } = renderHomePage({ store })
      const { offerer } = await waitForElements()

      // Then
      expect(
        within(offerer).getByText(offererWithNoPhysicalVenues.siren)
      ).toBeInTheDocument()
      expect(
        within(offerer).getByText(offererWithNoPhysicalVenues.name, {
          selector: 'span',
        })
      ).toBeInTheDocument()
      expect(
        within(offerer).getByText(offererWithNoPhysicalVenues.address, {
          exact: false,
        })
      ).toBeInTheDocument()
      expect(
        within(offerer).getByText(
          `${offererWithNoPhysicalVenues.postalCode} ${offererWithNoPhysicalVenues.city}`,
          { exact: false }
        )
      ).toBeInTheDocument()
    })

    it('should hide offerer informations on click on hide button', async () => {
      // Given
      const { waitForElements } = renderHomePage({ store })
      const { offerer } = await waitForElements()
      const hideButton = within(offerer).getByRole('button', {
        name: 'Masquer',
      })

      // When
      fireEvent.click(hideButton)

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

      pcapi.getOfferer.mockResolvedValue(offererWithPhysicalVenues)
      pcapi.getAllOfferersNames.mockResolvedValue([
        {
          id: offererWithPhysicalVenues.id,
          name: offererWithPhysicalVenues.name,
        },
      ])
    })

    it('should not display offerer informations', async () => {
      // When
      const { waitForElements } = renderHomePage({ store })
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
      const { waitForElements } = renderHomePage({ store })
      const { offerer } = await waitForElements()
      const showButton = within(offerer).getByRole('button', {
        name: 'Afficher',
      })

      // When
      fireEvent.click(showButton)

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
      pcapi.getOfferer.mockResolvedValue(nonValidatedOfferer)
      pcapi.getAllOfferersNames.mockResolvedValue([
        { name: nonValidatedOfferer.name, id: nonValidatedOfferer.id },
      ])
    })

    it('should warn user that offerer is being validated', async () => {
      // When
      const { waitForElements } = renderHomePage({ store })
      const { offerer } = await waitForElements()

      // Then
      expect(
        within(offerer).getByText('Votre structure est en cours de validation')
      ).toBeInTheDocument()
    })

    it('should allow user to view offerer informations', async () => {
      // When
      const { waitForElements } = renderHomePage({ store })
      const { offerer } = await waitForElements()

      // Then
      expect(
        within(offerer).getByText('Informations pratiques')
      ).toBeInTheDocument()
    })

    it('should allow user to add venue and offer', async () => {
      // When
      const { waitForElements } = renderHomePage({ store })
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
      pcapi.getAllOfferersNames.mockResolvedValue([
        {
          name: firstOffererByAlphabeticalOrder.name,
          id: firstOffererByAlphabeticalOrder.id,
        },
        { name: baseOfferers[0].name, id: baseOfferers[0].id },
      ])
      pcapi.getOfferer.mockRejectedValue({ status: 403 })
    })

    it('should warn user offerer is being validated', async () => {
      // When
      const { waitForElements } = renderHomePage({ store })
      await waitForElements()

      // Then
      expect(
        screen.getByText('Votre structure est en cours de validation')
      ).toBeInTheDocument()
    })

    it('should not allow user to view offerer informations', async () => {
      // When
      const { waitForElements } = renderHomePage({ store })
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
      const { waitForElements } = renderHomePage({ store })
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
      const { waitForElements } = renderHomePage({ store })
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
      pcapi.getAllOfferersNames.mockResolvedValue([
        { name: baseOfferers[0].name, id: baseOfferers[0].id },
        {
          name: firstOffererByAlphabeticalOrder.name,
          id: firstOffererByAlphabeticalOrder.id,
        },
      ])
      pcapi.getOfferer
        .mockResolvedValueOnce({
          ...firstOffererByAlphabeticalOrder,
          managedVenues: [virtualVenue, physicalVenue],
        })
        .mockRejectedValueOnce({ status: 403 })

      const { waitForElements } = renderHomePage({ store })
      await waitForElements()

      // When
      fireEvent.change(
        screen.getByDisplayValue(firstOffererByAlphabeticalOrder.name),
        {
          target: { value: baseOfferers[0].id },
        }
      )

      // Then
      expect(pcapi.getOfferer).toHaveBeenCalledTimes(2)

      await waitForElementToBeRemoved(() =>
        screen.getByRole('heading', { level: 3, name: 'Offres numériques' })
      )
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

  describe('when FF enforce siret is enabled', () => {
    beforeEach(() => {
      store = configureTestStore({
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
        features: {
          list: [
            { isActive: true, nameKey: 'ENFORCE_BANK_INFORMATION_WITH_SIRET' },
          ],
        },
      })
    })
    it('should display invalid business unit banner when a BU does not have a siret', async () => {
      firstOffererByAlphabeticalOrder = {
        ...firstOffererByAlphabeticalOrder,
        managedVenues: [
          {
            ...physicalVenue,
            businessUnitId: 2,
          },
        ],
      }
      pcapi.getOfferer.mockResolvedValue(firstOffererByAlphabeticalOrder)
      pcapi.getBusinessUnits.mockResolvedValue([
        {
          name: 'Business Unit #2',
          siret: null,
          id: 2,
          bic: 'BDFEFRPP',
          iban: 'FR9410010000000000000000022',
        },
      ])
      const { waitForElements } = renderHomePage({ store })
      const { offerer } = await waitForElements()

      expect(
        within(offerer).getByRole('button', {
          name: 'Masquer',
        })
      ).toBeInTheDocument()
      expect(
        within(offerer).getByText('Points de remboursement')
      ).toBeInTheDocument()
    })

    it('should display missing business unit banner when venue has no BU', async () => {
      firstOffererByAlphabeticalOrder = {
        ...firstOffererByAlphabeticalOrder,
        managedVenues: [
          {
            ...physicalVenue,
            businessUnitId: null,
          },
        ],
      }

      pcapi.getOfferer.mockResolvedValue(firstOffererByAlphabeticalOrder)
      pcapi.getBusinessUnits.mockResolvedValue([])

      const { waitForElements } = renderHomePage({ store })
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

    it('should not display missing business unit banner when virtual venue has no BU', async () => {
      firstOffererByAlphabeticalOrder = {
        ...firstOffererByAlphabeticalOrder,
        managedVenues: [
          {
            ...physicalVenue,
            businessUnitId: 2,
          },
          {
            ...virtualVenue,
            businessUnitId: null,
          },
        ],
      }

      pcapi.getOfferer.mockResolvedValue(firstOffererByAlphabeticalOrder)
      pcapi.getBusinessUnits.mockResolvedValue([
        {
          name: 'Business Unit #2',
          siret: '222222222222222222',
          id: 2,
          bic: 'BDFEFRPP',
          iban: 'FR9410010000000000000000022',
        },
      ])

      const { waitForElements } = renderHomePage({ store })
      const { offerer } = await waitForElements()

      const displayButton = within(offerer).getByRole('button', {
        name: 'Afficher',
      })
      expect(displayButton).toBeInTheDocument()

      // open offerer and wait that the block open.
      await userEvent.click(displayButton)
      const hideButton = await within(offerer).findByRole('button', {
        name: 'Masquer',
      })

      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_TOGGLE_HIDE_OFFERER_NAME,
        { isExpanded: false }
      )

      expect(
        within(offerer).queryByText('Coordonnées bancaires')
      ).not.toBeInTheDocument()

      await userEvent.click(hideButton)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        2,
        Events.CLICKED_TOGGLE_HIDE_OFFERER_NAME,
        { isExpanded: true }
      )
      expect(mockLogEvent).toHaveBeenCalledTimes(2)
    })
  })

  describe('when FF new bank informations creation', () => {
    beforeEach(() => {
      store = configureTestStore({
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
        features: {
          list: [
            {
              isActive: true,
              nameKey: 'ENABLE_NEW_BANK_INFORMATIONS_CREATION',
            },
          ],
        },
        app: { logEvent: mockLogEvent },
      })
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
      pcapi.getOfferer.mockResolvedValue(firstOffererByAlphabeticalOrder)

      const { waitForElements } = renderHomePage({ store })
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
      pcapi.getOfferer.mockResolvedValue(firstOffererByAlphabeticalOrder)

      const { waitForElements } = renderHomePage({ store })
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
