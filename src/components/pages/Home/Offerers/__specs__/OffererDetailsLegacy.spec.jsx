import '@testing-library/jest-dom'
import {
  act,
  fireEvent,
  render,
  screen,
  waitForElementToBeRemoved,
  within,
} from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import * as pcapi from 'repository/pcapi/pcapi'
import { configureTestStore } from 'store/testUtils'

import HomepageContainer from '../../HomepageContainer'
import { CREATE_OFFERER_SELECT_ID } from '../Offerers'

const mockHistoryPush = jest.fn()
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useHistory: () => ({
    push: mockHistoryPush,
  }),
}))

jest.mock('utils/config', () => ({
  DEMARCHES_SIMPLIFIEES_VENUE_RIB_UPLOAD_PROCEDURE_URL:
    'link/to/venue/demarchesSimplifiees/procedure',
}))

jest.mock('repository/pcapi/pcapi', () => ({
  getOfferer: jest.fn(),
  getAllOfferersNames: jest.fn(),
  getVenueStats: jest.fn(),
}))

const renderHomePage = async () => {
  const store = configureTestStore({
    data: {
      users: [
        {
          id: 'fake_id',
          firstName: 'John',
          lastName: 'Do',
          email: 'john.do@dummy.xyz',
          phoneNumber: '01 00 00 00 00',
        },
      ],
    },
  })
  return await act(async () => {
    await render(
      <Provider store={store}>
        <MemoryRouter>
          <HomepageContainer />
        </MemoryRouter>
      </Provider>
    )
  })
}

describe('offererDetailsLegacy', () => {
  let baseOfferers
  let firstOffererByAlphabeticalOrder
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
        city: 'Drancy',
        id: 'FQ',
        isValidated: true,
        name: 'Club Dorothy',
        postalCode: '93700',
        siren: '222222222',
        bic: 'test bic 02',
        iban: 'test iban 02',
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
        city: 'Cayenne',
        name: 'Bar des amis',
        id: 'GE',
        isValidated: true,
        postalCode: '97300',
        siren: '111111111',
        bic: 'test bic 01',
        iban: 'test iban 01',
        managedVenues: [virtualVenue, physicalVenue, physicalVenueWithPublicName],
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
  })

  it('should display offerer select', async () => {
    await renderHomePage()
    const showButton = screen.getByRole('button', { name: 'Afficher' })
    fireEvent.click(showButton)

    expect(screen.getByDisplayValue(firstOffererByAlphabeticalOrder.name)).toBeInTheDocument()
  })

  it('should not warn user when offerer is validated', async () => {
    // Given
    await renderHomePage()
    const showButton = screen.getByRole('button', { name: 'Afficher' })

    // When
    fireEvent.click(showButton)

    // Then
    expect(screen.queryByText('Votre structure est en cours de validation')).not.toBeInTheDocument()
  })

  it('should display first offerer informations', async () => {
    await renderHomePage()
    const showButton = screen.getByRole('button', { name: 'Afficher' })
    fireEvent.click(showButton)

    const selectedOfferer = firstOffererByAlphabeticalOrder
    expect(screen.getByText(selectedOfferer.siren)).toBeInTheDocument()
    expect(screen.getByText(selectedOfferer.name, { selector: 'span' })).toBeInTheDocument()
    expect(screen.getByText(selectedOfferer.address, { exact: false })).toBeInTheDocument()
    expect(
      screen.getByText(`${selectedOfferer.postalCode} ${selectedOfferer.city}`, { exact: false })
    ).toBeInTheDocument()
  })

  it('should display offerer venues informations', async () => {
    await renderHomePage()
    const showButton = screen.getByRole('button', { name: 'Afficher' })
    fireEvent.click(showButton)

    const selectedOfferer = firstOffererByAlphabeticalOrder
    const virtualVenueTitle = screen.getByText('Offres numériques')
    expect(virtualVenueTitle).toBeInTheDocument()

    const physicalVenueTitle = screen.getByText(selectedOfferer.managedVenues[1].name)
    expect(physicalVenueTitle).toBeInTheDocument()
    const physicalVenueContainer = physicalVenueTitle.closest('div')
    expect(
      within(physicalVenueContainer).getByText('Modifier', { exact: false })
    ).toBeInTheDocument()

    const secondOfflineVenueTitle = screen.getByText(selectedOfferer.managedVenues[2].publicName)
    expect(secondOfflineVenueTitle).toBeInTheDocument()
  })

  it('should not display virtual venue informations when no virtual offers', async () => {
    // Given
    firstOffererByAlphabeticalOrder.managedVenues = [
      {
        ...virtualVenue,
        nOffers: 0,
      },
      physicalVenue,
    ]

    // When
    await renderHomePage()

    // Then
    expect(
      screen.queryByRole('heading', { level: 3, name: 'Offres numériques', exact: false })
    ).not.toBeInTheDocument()
  })

  describe('when selected offerer change', () => {
    let newSelectedOfferer
    beforeEach(async () => {
      const selectedOffer = firstOffererByAlphabeticalOrder
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
      await renderHomePage()
      pcapi.getOfferer.mockResolvedValue(newSelectedOfferer)
      await act(async () => {
        await fireEvent.change(screen.getByDisplayValue(selectedOffer.name), {
          target: { value: newSelectedOfferer.id },
        })
      })
      const showButton = screen.getByRole('button', { name: 'Afficher' })
      fireEvent.click(showButton)
    })

    it('should change displayed offerer informations', async () => {
      expect(screen.getByText(newSelectedOfferer.siren)).toBeInTheDocument()
      expect(screen.getByText(newSelectedOfferer.name, { selector: 'span' })).toBeInTheDocument()
      expect(screen.getByText(newSelectedOfferer.address, { exact: false })).toBeInTheDocument()
      expect(
        screen.getByText(`${newSelectedOfferer.postalCode} ${newSelectedOfferer.city}`, {
          exact: false,
        })
      ).toBeInTheDocument()
    })

    it('should display new offerer venues informations', async () => {
      const virtualVenueTitle = screen.getByText('Offres numériques')
      expect(virtualVenueTitle).toBeInTheDocument()

      const physicalVenueTitle = screen.getByText(newSelectedOfferer.managedVenues[1].name)
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
      const selectedOffer = firstOffererByAlphabeticalOrder
      await renderHomePage()

      // When
      await act(async () => {
        await fireEvent.change(screen.getByDisplayValue(selectedOffer.name), {
          target: { value: CREATE_OFFERER_SELECT_ID },
        })
      })

      // Then
      expect(mockHistoryPush).toHaveBeenCalledWith('/structures/creation')
    })
  })

  describe("when offerer doesn't have bank informations", () => {
    it('should display bank warning if offerer has physical venue without bank informations', async () => {
      // Given
      baseOfferers = [
        {
          ...firstOffererByAlphabeticalOrder,
          bic: '',
          iban: '',
          demarchesSimplifieesApplicationId: '',
          managedVenues: [virtualVenue, { ...physicalVenue, iban: '', bic: '' }],
        },
      ]
      pcapi.getOfferer.mockResolvedValue(baseOfferers[0])

      // When
      await renderHomePage()
      const showButton = screen.getByRole('button', { name: 'Afficher' })
      fireEvent.click(showButton)

      // Then
      const link = screen.getByRole('link', {
        name: 'Renseignez les coordonnées bancaires',
      })
      expect(link).toBeInTheDocument()
      const warningIcons = screen.getAllByAltText('Informations bancaires manquantes')
      let nbWarningIcons = 0
      nbWarningIcons += 1 // in offerers header
      nbWarningIcons += 1 // in bank account card title
      expect(warningIcons).toHaveLength(nbWarningIcons)
    })

    it("shouldn't display bank warning if all physical venues have bank informations", async () => {
      physicalVenue = {
        ...physicalVenue,
        bic: 'fake_bic',
        iban: 'fake_iban',
      }
      physicalVenueWithPublicName = {
        ...physicalVenueWithPublicName,
        demarchesSimplifieesApplicationId: 'fake_demarchesSimplifieesApplicationId',
      }
      virtualVenue = {
        ...virtualVenue,
        nOffers: 0,
      }
      baseOfferers = [
        {
          ...firstOffererByAlphabeticalOrder,
          bic: '',
          iban: '',
          managedVenues: [virtualVenue, physicalVenue, physicalVenueWithPublicName],
        },
      ]
      pcapi.getOfferer.mockResolvedValue(firstOffererByAlphabeticalOrder)
      await renderHomePage()

      const warningIcons = await screen.queryByAltText('Informations bancaires manquantes')
      expect(warningIcons).not.toBeInTheDocument()
    })

    it('should display file information for pending registration', async () => {
      baseOfferers = [
        {
          ...firstOffererByAlphabeticalOrder,
          bic: '',
          iban: '',
          demarchesSimplifieesApplicationId: 'demarchesSimplifieesApplication_fake_id',
        },
      ]
      pcapi.getOfferer.mockResolvedValue(baseOfferers[0])
      await renderHomePage()

      const showButton = screen.getByRole('button', { name: 'Afficher' })
      fireEvent.click(showButton)
      expect(screen.getByRole('link', { name: 'Voir le dossier' })).toBeInTheDocument()
      const warningIcons = await screen.queryByAltText('Informations bancaires manquantes')
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
        address: 'LA COULÉE D’OR',
        city: 'Cayenne',
        name: 'Bar des amis',
        id: 'GE',
        isValidated: true,
        managedVenues: [virtualVenue],
        postalCode: '97300',
        siren: '111111111',
        bic: 'test bic 01',
        iban: 'test iban 01',
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
      await renderHomePage()

      // Then
      expect(screen.getByText(offererWithNoPhysicalVenues.siren)).toBeInTheDocument()
      expect(
        screen.getByText(offererWithNoPhysicalVenues.name, { selector: 'span' })
      ).toBeInTheDocument()
      expect(
        screen.getByText(offererWithNoPhysicalVenues.address, { exact: false })
      ).toBeInTheDocument()
      expect(
        screen.getByText(
          `${offererWithNoPhysicalVenues.postalCode} ${offererWithNoPhysicalVenues.city}`,
          { exact: false }
        )
      ).toBeInTheDocument()
    })

    it('should hide offerer informations on click on hide button', async () => {
      // Given
      await renderHomePage()
      const hideButton = screen.getByRole('button', { name: 'Masquer' })

      // When
      fireEvent.click(hideButton)

      //Then
      const selectedOffererAddress = `${offererWithNoPhysicalVenues.address} ${offererWithNoPhysicalVenues.postalCode} ${offererWithNoPhysicalVenues.city}`
      expect(screen.queryByText(offererWithNoPhysicalVenues.siren)).not.toBeInTheDocument()
      expect(
        screen.queryByText(offererWithNoPhysicalVenues.name, { selector: 'span' })
      ).not.toBeInTheDocument()
      expect(screen.queryByText(selectedOffererAddress)).not.toBeInTheDocument()
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
        address: 'LA COULÉE D’OR',
        city: 'Cayenne',
        name: 'Bar des amis',
        id: 'GE',
        isValidated: true,
        managedVenues: offererVenues,
        postalCode: '97300',
        siren: '111111111',
        bic: 'test bic 01',
        iban: 'test iban 01',
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
      await renderHomePage()

      // Then
      const selectedOffererAddress = `${offererWithPhysicalVenues.address} ${offererWithPhysicalVenues.postalCode} ${offererWithPhysicalVenues.city}`
      expect(screen.queryByText(offererWithPhysicalVenues.siren)).not.toBeInTheDocument()
      expect(
        screen.queryByText(offererWithPhysicalVenues.name, { selector: 'span' })
      ).not.toBeInTheDocument()
      expect(screen.queryByText(selectedOffererAddress)).not.toBeInTheDocument()
    })

    it('should show offerer informations on click on show button', async () => {
      // Given
      await renderHomePage()
      const showButton = screen.getByRole('button', { name: 'Afficher' })

      // When
      fireEvent.click(showButton)

      //Then
      expect(screen.getByText(offererWithPhysicalVenues.siren)).toBeInTheDocument()
      expect(
        screen.getByText(offererWithPhysicalVenues.name, { selector: 'span' })
      ).toBeInTheDocument()
      expect(
        screen.getByText(offererWithPhysicalVenues.address, { exact: false })
      ).toBeInTheDocument()
      expect(
        screen.getByText(
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
      await renderHomePage()

      // Then
      expect(screen.getByText('Votre structure est en cours de validation')).toBeInTheDocument()
    })

    it('should allow user to view offerer informations', async () => {
      // When
      await renderHomePage()

      // Then
      expect(screen.getByText('Informations pratiques')).toBeInTheDocument()
    })

    it('should allow user to add venue and virtual offer', async () => {
      // When
      await renderHomePage()

      // Then
      expect(screen.getByRole('link', { name: 'Créer un lieu' })).toBeInTheDocument()
      expect(screen.getByRole('link', { name: 'Créer une offre numérique' })).toBeInTheDocument()
    })
  })

  describe('when user attachment to offerer is not yet validated', () => {
    beforeEach(() => {
      pcapi.getAllOfferersNames.mockResolvedValue([
        { name: firstOffererByAlphabeticalOrder.name, id: firstOffererByAlphabeticalOrder.id },
        { name: baseOfferers[0].name, id: baseOfferers[0].id },
      ])
      pcapi.getOfferer.mockRejectedValue({ status: 403 })
    })

    it('should warn user offerer is being validated', async () => {
      // When
      await renderHomePage()

      // Then
      expect(screen.getByText('Votre structure est en cours de validation')).toBeInTheDocument()
    })

    it('should not allow user to view offerer informations', async () => {
      // When
      await renderHomePage()

      // Then
      expect(screen.queryByText('Informations pratiques')).not.toBeInTheDocument()
      expect(screen.queryByText('Coordonnées bancaires')).not.toBeInTheDocument()
    })

    it('should not allow user to update offerer informations', async () => {
      // When
      await renderHomePage()

      // Then
      const [offererUpdateButton] = screen.getAllByRole('button', { name: 'Modifier' })
      expect(offererUpdateButton).toBeInTheDocument()
      expect(offererUpdateButton).toBeDisabled()
    })

    it('should not allow user to add venue and virtual offer', async () => {
      // When
      await renderHomePage()

      // Then
      expect(screen.queryByRole('link', { name: 'Créer un lieu' })).not.toBeInTheDocument()
      expect(
        screen.queryByRole('link', { name: 'Créer une offre numérique' })
      ).not.toBeInTheDocument()
    })

    it('should not show venues of previously selected offerer', async () => {
      // Given
      pcapi.getAllOfferersNames.mockResolvedValue([
        { name: baseOfferers[0].name, id: baseOfferers[0].id },
        { name: firstOffererByAlphabeticalOrder.name, id: firstOffererByAlphabeticalOrder.id },
      ])
      pcapi.getOfferer
        .mockResolvedValueOnce({
          ...firstOffererByAlphabeticalOrder,
          managedVenues: [virtualVenue, physicalVenue],
        })
        .mockRejectedValueOnce({ status: 403 })

      await renderHomePage()

      // When
      fireEvent.change(screen.getByDisplayValue(firstOffererByAlphabeticalOrder.name), {
        target: { value: baseOfferers[0].id },
      })

      // Then
      expect(pcapi.getOfferer).toHaveBeenCalledTimes(2)
      await waitForElementToBeRemoved(() =>
        screen.getByRole('heading', { level: 3, name: 'Offres numériques' })
      )
      const previouslySelectedOfferersPhysicalVenueName = screen.queryByRole('heading', {
        level: 3,
        name: physicalVenue.name,
      })
      expect(previouslySelectedOfferersPhysicalVenueName).not.toBeInTheDocument()
    })
  })
})
