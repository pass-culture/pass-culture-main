import '@testing-library/jest-dom'

import * as pcapi from 'repository/pcapi/pcapi'

import { MemoryRouter, Route } from 'react-router'
import { render, screen } from '@testing-library/react'

import NotificationContainer from 'components/layout/Notification/NotificationContainer'
import OfferLayout from '../../OfferLayout'
import { Provider } from 'react-redux'
import React from 'react'
import { api } from 'apiClient/api'
import { configureTestStore } from 'store/testUtils'
import { getOfferInputForField } from './helpers'
import userEvent from '@testing-library/user-event'

jest.mock('repository/pcapi/pcapi', () => ({
  ...jest.requireActual('repository/pcapi/pcapi'),
  updateOffer: jest.fn(),
  getUserValidatedOfferersNames: jest.fn(),
  getVenue: jest.fn(),
  getVenuesForOfferer: jest.fn(),
  loadCategories: jest.fn(),
  loadStocks: jest.fn(),
  loadTypes: jest.fn(),
  postThumbnail: jest.fn(),
}))

const renderOfferCreation = async (
  props,
  url = '/offre/ABC12/individuel/creation',
  storeOverride = {}
) => {
  const defaultStore = {
    features: {
      initialized: true,
      list: [
        {
          isActive: true,
          name: 'ENABLE_ISBN_REQUIRED_IN_LIVRE_EDITION_OFFER_CREATION',
          nameKey: 'ENABLE_ISBN_REQUIRED_IN_LIVRE_EDITION_OFFER_CREATION',
        },
        {
          isActive: true,
          name: 'OFFER_FORM_V3',
          nameKey: 'OFFER_FORM_V3',
        },
        {
          isActive: true,
          name: 'OFFER_FORM_SUMMARY_PAGE',
          nameKey: 'OFFER_FORM_SUMMARY_PAGE',
        },
      ],
    },
    data: {
      users: [
        {
          publicName: 'François',
          isAdmin: false,
          email: 'francois@example.com',
        },
      ],
    },
    user: { initialized: true },
  }
  const store = configureTestStore({
    ...defaultStore,
    ...storeOverride,
  })
  const rtlRenderReturn = render(
    <Provider store={store}>
      <MemoryRouter initialEntries={[url]}>
        <Route
          path={[
            '/offre/creation/individuel',
            '/offre/:offerId([A-Z0-9]+)/individuel',
          ]}
        >
          <>
            <OfferLayout {...props} />
            <NotificationContainer />
          </>
        </Route>
      </MemoryRouter>
    </Provider>
  )

  return rtlRenderReturn
}

describe('offerCreation - navigate backward', () => {
  let offer
  let offerers
  let offerVenue
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

    const categories = {
      categories: [
        {
          id: 'CAT1',
          proLabel: 'Categorie 1',
          isSelectable: true,
        },
        {
          id: 'CAT2',
          proLabel: 'Categorie 2',
          isSelectable: true,
        },
      ],
      subcategories: [
        {
          id: 'SUB_CAT1',
          categoryId: 'CAT1',
          proLabel: 'Sous-categorie 1',
          appLabel: 'Support physique (DVD, Bluray...)',
          searchGroup: 'Films, séries, podcasts',
          isEvent: false,
          conditionalFields: ['author', 'musicType', 'musicType', 'performer'],
          canExpire: true,
          canBeDuo: false,
          canBeEducational: false,
          onlineOfflinePlatform: 'OFFLINE',
          isDigitalDeposit: false,
          isPhysicalDeposit: true,
          reimbursementRule: 'STANDARD',
          isSelectable: true,
        },
        {
          id: 'SUB_CAT2',
          categoryId: 'CAT2',
          proLabel: 'Sous-categorie 2',
          appLabel: 'Abonnement médiathèque',
          searchGroup: 'Films, séries, podcasts',
          isEvent: false,
          conditionalFields: [],
          canExpire: true,
          canBeDuo: false,
          canBeEducational: false,
          onlineOfflinePlatform: 'OFFLINE',
          isDigitalDeposit: false,
          isPhysicalDeposit: true,
          reimbursementRule: 'STANDARD',
          isSelectable: true,
        },
      ],
    }

    const offerOfferer = {
      id: 'BA',
      name: 'La structure',
    }

    offerVenue = {
      id: 'AB',
      isVirtual: false,
      managingOfferer: offerOfferer,
      managingOffererId: offerOfferer.id,
      name: 'Le lieu',
      offererName: 'La structure',
      bookingEmail: 'venue@example.com',
      withdrawalDetails: null,
      audioDisabilityCompliant: null,
      mentalDisabilityCompliant: null,
      motorDisabilityCompliant: null,
      visualDisabilityCompliant: null,
    }

    offer = {
      id: 'ABC12',
      nonHumanizedId: 111,
      subcategoryId: 'SUB_CAT1',
      name: 'My edited offer',
      venue: offerVenue,
      venueId: offerVenue.id,
      thumbUrl: null,
      description: 'My edited description',
      withdrawalDetails: 'My edited withdrawal details',
      status: 'SOLD_OUT',
      extraData: {
        musicType: '501',
        musicSubType: '502',
      },
      audioDisabilityCompliant: false,
      mentalDisabilityCompliant: false,
      motorDisabilityCompliant: false,
      visualDisabilityCompliant: false,
    }

    jest.spyOn(api, 'getOffer').mockResolvedValue(offer)
    pcapi.getUserValidatedOfferersNames.mockResolvedValue(offerers)
    pcapi.getVenuesForOfferer.mockResolvedValue(venues)
    pcapi.getVenue.mockReturnValue(Promise.resolve())
    pcapi.loadCategories.mockResolvedValue(categories)
    jest.spyOn(window, 'scrollTo').mockImplementation()
  })

  it('should display creation layout on creation url with offer id', async () => {
    await renderOfferCreation(props)
    await getOfferInputForField('categoryId')

    expect(screen.getByRole('heading', { name: 'Créer une offre' }))
    expect(api.getOffer).toHaveBeenCalledWith(offer.id)
  })

  it('should display creation layout on creation url with offer id', async () => {
    await renderOfferCreation(props)
    await getOfferInputForField('categoryId')

    expect(await getOfferInputForField('categoryId')).toHaveValue('CAT1')
    expect(await getOfferInputForField('subcategoryId')).toHaveValue(
      offer.subcategoryId
    )
    expect(await getOfferInputForField('musicType')).toHaveValue('501')
    expect(await getOfferInputForField('musicSubType')).toHaveValue('502')
    expect(await getOfferInputForField('name')).toHaveValue(offer.name)
    expect(await getOfferInputForField('description')).toHaveValue(
      offer.description
    )
    expect(await getOfferInputForField('offererId')).toHaveValue(
      offer.venue.managingOffererId
    )
    expect(await getOfferInputForField('venueId')).toHaveValue(offer.venue.id)
  })

  it('creation route with offer id should not allow all fields edition', async () => {
    await renderOfferCreation(props)
    await getOfferInputForField('categoryId')

    expect(await getOfferInputForField('categoryId')).toBeDisabled()
    expect(await getOfferInputForField('subcategoryId')).toBeDisabled()
    expect(await getOfferInputForField('musicType')).toBeDisabled()
    expect(await getOfferInputForField('musicSubType')).toBeDisabled()
    expect(await getOfferInputForField('name')).not.toBeDisabled()
    expect(await getOfferInputForField('description')).not.toBeDisabled()
    expect(await getOfferInputForField('offererId')).toBeDisabled()
    expect(await getOfferInputForField('venueId')).toBeDisabled()
  })

  it('creation route with offer id submit should redirect to stock form', async () => {
    await renderOfferCreation(props)
    await getOfferInputForField('categoryId')

    // FIXME: should call creation patch route when available.
    pcapi.updateOffer.mockResolvedValue({})
    pcapi.loadStocks.mockResolvedValue({ stocks: [] })
    await userEvent.click(screen.getByText('Étape suivante'))

    // TODO: expect: creation route with offer id submit should call the right api route (patch all fields)
    expect(
      await screen.findByRole('heading', { name: 'Stock et prix' })
    ).toBeInTheDocument()
  })

  it('creation step should be clicable from stock form, it link to creation route with offer id', async () => {
    pcapi.loadStocks.mockResolvedValue({ stocks: [] })
    await renderOfferCreation(props, '/offre/ABC12/individuel/creation/stocks')
    await screen.findByRole('heading', {
      name: 'Stock et prix',
    })

    await userEvent.click(screen.getByText("Détails de l'offre"))

    expect(
      await screen.findByRole('heading', { name: 'Type d’offre' })
    ).toBeInTheDocument()
  })
})
