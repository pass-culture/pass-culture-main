import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter, Route } from 'react-router'

import { api } from 'apiClient/api'
import { Events } from 'core/FirebaseEvents/constants'
import { OFFER_WITHDRAWAL_TYPE_OPTIONS } from 'core/Offers'
import * as useAnalytics from 'hooks/useAnalytics'
import { Notification } from 'new_components/Notification'
import { configureTestStore } from 'store/testUtils'
import { ButtonLink } from 'ui-kit'
import { loadFakeApiCategories } from 'utils/fakeApi'

import OfferLayout from '../../OfferLayout'

import { getOfferInputForField, sidebarDisplayed } from './helpers'

const mockLogEvent = jest.fn()

Element.prototype.scrollIntoView = () => {}

jest.mock('repository/pcapi/pcapi', () => ({
  ...jest.requireActual('repository/pcapi/pcapi'),
  postThumbnail: jest.fn(),
}))

jest.mock('apiClient/api', () => ({
  api: {
    postOffer: jest.fn(),
    getOffer: jest.fn(),
    listOfferersNames: jest.fn(),
    getVenues: jest.fn(),
    getVenue: jest.fn(),
    getCategories: jest.fn(),
    getStocks: jest.fn(),
  },
}))

const store = configureTestStore({
  features: {
    initialized: true,
    list: [
      {
        isActive: true,
        nameKey: 'OFFER_DRAFT_ENABLED',
      },
    ],
  },
  user: {
    currentUser: {
      publicName: 'François',
      isAdmin: false,
      email: 'francois@example.com',
    },
  },
})

const renderOffers = async (props, queryParams = null) => {
  const rtlRenderReturn = render(
    <Provider store={store}>
      <MemoryRouter
        initialEntries={[
          { pathname: '/offre/creation/individuel', search: queryParams },
        ]}
      >
        <Route
          path={[
            '/offre/creation/individuel',
            '/offre/:offerId([A-Z0-9]+)/individuel',
          ]}
        >
          <>
            <OfferLayout {...props} />
            <ButtonLink link={{ to: '/lapin', isExternal: false }}>
              Display exit modal
            </ButtonLink>
            <Notification />
          </>
        </Route>
      </MemoryRouter>
    </Provider>
  )
  await getOfferInputForField('categoryId')

  return rtlRenderReturn
}

describe('offerDetails - Creation - pro user - tracking', () => {
  let offerers
  let props
  let venues

  beforeEach(() => {
    props = {
      setShowThumbnailForm: jest.fn(),
    }
    const offerer1Id = 'BA'
    const offerer2Id = 'BAC'

    offerers = [
      {
        id: offerer1Id,
        name: 'La structure',
      },
      {
        id: offerer2Id,
        name: "L'autre structure",
      },
    ]

    venues = [
      {
        id: 'AB',
        isVirtual: false,
        managingOffererId: offerer1Id,
        name: 'Le lieu',
        offererName: 'La structure',
        bookingEmail: 'lieu@example.com',
        withdrawalDetails: 'Modalité retrait 1',
        managingOfferer: { name: 'My offerer', id: 'ID' },
      },
      {
        id: 'ABC',
        isVirtual: false,
        managingOffererId: offerer2Id,
        name: "L'autre lieu",
        offererName: "L'autre structure",
        bookingEmail: 'autre-lieu@example.com',
        withdrawalDetails: 'Modalité retrait 2',
        audioDisabilityCompliant: true,
        mentalDisabilityCompliant: true,
        motorDisabilityCompliant: true,
        visualDisabilityCompliant: true,
      },
      {
        id: 'ABCD',
        isVirtual: true,
        managingOffererId: offerer2Id,
        name: "L'autre lieu (Offre numérique)",
        offererName: "L'autre structure",
        withdrawalDetails: null,
      },
      {
        id: 'ABCDE',
        isVirtual: true,
        managingOffererId: offerer2Id,
        name: "L'autre lieu du lieu",
        offererName: "L'autre structure",
        publicName: "Le nom d'usage de l'autre autre lieu",
        withdrawalDetails: 'Modalité retrait 3',
      },
    ]

    api.listOfferersNames.mockResolvedValue({ offerersNames: offerers })
    api.getVenues.mockResolvedValue({ venues })
    api.getVenue.mockReturnValue(Promise.resolve())
    api.postOffer.mockResolvedValue({})
    loadFakeApiCategories()
    jest.spyOn(api, 'getOffer').mockResolvedValue({
      status: 'DRAFT',
      venue: {
        departementCode: 93,
      },
    })
    api.getStocks.mockResolvedValue({ stocks: [] })
    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
  })

  describe('when submitting form', () => {
    it('should call API with offer data', async () => {
      // Given
      api.getVenue.mockReturnValue(venues[0])
      await renderOffers(props)
      await userEvent.selectOptions(
        await screen.findByLabelText(/Catégorie/),
        'MUSIQUE_LIVE'
      )
      await userEvent.selectOptions(
        await screen.findByLabelText(/Sous-catégorie/),
        'CONCERT'
      )
      await userEvent.click(
        await screen.findByLabelText(/Évènement sans billet/)
      )
      await userEvent.type(
        await screen.findByLabelText(/Titre de l'offre/),
        'Ma petite offre'
      )
      await userEvent.type(
        screen.getByLabelText(/Description/),
        'Pas si petite que ça'
      )
      await userEvent.selectOptions(screen.getByLabelText(/Lieu/), venues[0].id)
      await userEvent.click(screen.getByLabelText(/Visuel/))
      await userEvent.type(screen.getByLabelText(/Durée/), '1:30')
      await userEvent.type(
        screen.getByLabelText(/URL de votre site ou billetterie/),
        'http://example.net'
      )
      await userEvent.selectOptions(
        screen.getByLabelText(/Genre musical/),
        '501'
      )
      await userEvent.selectOptions(screen.getByLabelText(/Sous genre/), '502')
      await userEvent.click(screen.getByLabelText(/Aucune/))
      await userEvent.type(
        screen.getByLabelText(/Interprète/),
        'TEST PERFORMER NAME'
      )
      await userEvent.type(
        screen.getByLabelText(/Informations de retrait/),
        'À venir chercher sur place.'
      )

      await sidebarDisplayed()

      const createdOffer = {
        name: 'Ma petite offre',
        description: 'Pas si petite que ça',
        venueId: venues[0].id,
        durationMinutes: '1:30',
        isDuo: false,
        audioDisabilityCompliant: false,
        mentalDisabilityCompliant: false,
        motorDisabilityCompliant: false,
        visualDisabilityCompliant: true,
        externalTicketOfficeUrl: 'http://example.net',
        subcategoryId: 'CONCERT',
        extraData: {
          musicType: '501',
          musicSubType: '502',
          performer: 'TEST PERFORMER NAME',
        },
        withdrawalDetails: 'À venir chercher sur place.',
        withdrawalType: OFFER_WITHDRAWAL_TYPE_OPTIONS.NO_TICKET,
        id: 'CREATED_ID',
        stocks: [],
        venue: venues[0],
        status: 'ACTIVE',
        bookingEmail: null,
      }

      api.postOffer.mockResolvedValue(createdOffer)
      const submitButton = screen.getByText('Étape suivante')

      // When
      await userEvent.click(submitButton)
      await screen.findByText('Créer une offre')

      // Then
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_OFFER_FORM_NAVIGATION,
        {
          from: 'details',
          isDraft: true,
          isEdition: false,
          offerId: 'CREATED_ID',
          to: 'stocks',
          used: 'StickyButtons',
        }
      )
    })
    it('should save offer on save draft button click', async () => {
      api.getVenue.mockReturnValue(venues[0])
      await renderOffers(props)

      await userEvent.selectOptions(
        await screen.findByLabelText(/Catégorie/),
        'MUSIQUE_LIVE'
      )
      await userEvent.selectOptions(
        await screen.findByLabelText(/Sous-catégorie/),
        'CONCERT'
      )
      await userEvent.click(
        await screen.findByLabelText(/Évènement sans billet/)
      )
      await userEvent.type(
        await screen.findByLabelText(/Titre de l'offre/),
        'Ma petite offre'
      )
      await userEvent.type(
        screen.getByLabelText(/Description/),
        'Pas si petite que ça'
      )
      await userEvent.selectOptions(screen.getByLabelText(/Lieu/), venues[0].id)
      await userEvent.click(screen.getByLabelText(/Visuel/))
      await userEvent.type(screen.getByLabelText(/Durée/), '1:30')
      await userEvent.type(
        screen.getByLabelText(/URL de votre site ou billetterie/),
        'http://example.net'
      )
      await userEvent.selectOptions(
        screen.getByLabelText(/Genre musical/),
        '501'
      )
      await userEvent.selectOptions(screen.getByLabelText(/Sous genre/), '502')
      await userEvent.click(screen.getByLabelText(/Aucune/))
      await userEvent.type(
        screen.getByLabelText(/Interprète/),
        'TEST PERFORMER NAME'
      )
      await userEvent.type(
        screen.getByLabelText(/Informations de retrait/),
        'À venir chercher sur place.'
      )

      await sidebarDisplayed()

      const createdOffer = {
        name: 'Ma petite offre',
        description: 'Pas si petite que ça',
        venueId: venues[0].id,
        durationMinutes: '1:30',
        isDuo: false,
        audioDisabilityCompliant: false,
        mentalDisabilityCompliant: false,
        motorDisabilityCompliant: false,
        visualDisabilityCompliant: true,
        externalTicketOfficeUrl: 'http://example.net',
        subcategoryId: 'CONCERT',
        extraData: {
          musicType: '501',
          musicSubType: '502',
          performer: 'TEST PERFORMER NAME',
        },
        withdrawalDetails: 'À venir chercher sur place.',
        withdrawalType: OFFER_WITHDRAWAL_TYPE_OPTIONS.NO_TICKET,
        id: 'CREATED_ID',
        stocks: [],
        venue: venues[0],
        status: 'ACTIVE',
        bookingEmail: null,
      }

      api.postOffer.mockResolvedValue(createdOffer)
      api.getOffer.mockResolvedValue(createdOffer)
      const submitButton = screen.getByText('Sauvegarder le brouillon')

      // When
      await userEvent.click(submitButton)

      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_OFFER_FORM_NAVIGATION,
        {
          from: 'details',
          isDraft: true,
          isEdition: false,
          offerId: 'CREATED_ID',
          to: 'details',
          used: 'DraftButtons',
        }
      )
    })
  })

  it('should track when exiting confirmation modal', async () => {
    // Given
    await renderOffers(props)

    // When
    await userEvent.click(await screen.findByText('Display exit modal'))
    await userEvent.click(await screen.findByText('Quitter'))

    // Then
    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'details',
        isDraft: true,
        isEdition: false,
        offerId: undefined,
        to: '/lapin',
        used: 'RouteLeavingGuard',
      }
    )
  })

  it('should track when clicking on annuler et quitter', async () => {
    // Given
    await renderOffers(props)

    // When
    await userEvent.click(await screen.findByText('Annuler et quitter'))
    await userEvent.click(await screen.findByText('Quitter'))

    // Then
    expect(mockLogEvent).toHaveBeenCalledTimes(2)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'details',
        isDraft: true,
        isEdition: false,
        offerId: undefined,
        to: 'Offers',
        used: 'StickyButtons',
      }
    )
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      2,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'details',
        isDraft: true,
        isEdition: false,
        offerId: undefined,
        to: '/offres',
        used: 'RouteLeavingGuard',
      }
    )
  })
})
