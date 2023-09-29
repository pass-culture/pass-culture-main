import { screen } from '@testing-library/react'
import React from 'react'
import { generatePath, Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import {
  GetIndividualOfferResponseModel,
  OfferStatus,
  SubcategoryIdEnum,
} from 'apiClient/v1'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferBreadcrumb/constants'
import { CATEGORY_STATUS, OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { getIndividualOfferPath } from 'core/Offers/utils/getIndividualOfferUrl'
import {
  GetIndividualOfferFactory,
  getOfferVenueFactory,
  offererFactory,
} from 'utils/apiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import IndividualOfferWizard from '../IndividualOfferWizard'

const offerer = offererFactory({ id: 12 })
const venue = getOfferVenueFactory(undefined, offerer)
const apiOffer: GetIndividualOfferResponseModel = GetIndividualOfferFactory(
  undefined,
  undefined,
  venue
)

const renderIndividualOfferWizardRoute = (
  storeOverrides: any,
  url = '/offre/v3'
) =>
  renderWithProviders(
    <Routes>
      <Route
        path="offre/individuelle/:offerId/*"
        element={<IndividualOfferWizard />}
      />
    </Routes>,
    {
      storeOverrides,
      initialRouterEntries: [url],
    }
  )

describe('IndividualOfferWizard', () => {
  let store: any

  beforeEach(() => {
    store = {
      user: {
        initialized: true,
        currentUser: {
          isAdmin: true,
          email: 'email@example.com',
        },
      },
    }
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({ offerersNames: [] })
    vi.spyOn(api, 'getVenues').mockResolvedValue({ venues: [] })
    vi.spyOn(api, 'getCategories').mockResolvedValue({
      categories: [],
      subcategories: [],
    })
    vi.spyOn(api, 'getOffer').mockResolvedValue(apiOffer)
    vi.spyOn(api, 'listOffers').mockResolvedValue([
      {
        id: 1,
        status: OfferStatus.ACTIVE,
        isActive: true,
        hasBookingLimitDatetimesPassed: false,
        isEducational: false,
        name: 'name',
        isEvent: false,
        venue: {
          name: 'venue',
          offererName: 'offerer',
          isVirtual: false,
          id: 1,
        },
        stocks: [],
        isEditable: true,
        isShowcase: false,
        isThing: false,
        subcategoryId: SubcategoryIdEnum.VOD,
      },
    ])
  })

  it('should initialize context with api with offererId on query', async () => {
    await renderIndividualOfferWizardRoute(
      store,
      generatePath(
        getIndividualOfferPath({
          step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
          mode: OFFER_WIZARD_MODE.CREATION,
          isCreation: true,
        })
      ) +
        '?structure=' +
        offerer.id
    )
    expect(
      await screen.findByRole('heading', { name: 'Créer une offre' })
    ).toBeInTheDocument()
    expect(await screen.findByLabelText('Catégorie')).toBeInTheDocument()
    expect(api.getVenues).toHaveBeenCalledWith(
      null, // validated,
      true, // activeOfferersOnly,
      offerer.id // offererId
    )
    expect(api.listOfferersNames).toHaveBeenCalledWith(
      null, // validated
      null, // validatedForUser
      offerer.id // offererId
    )

    expect(api.getCategories).toHaveBeenCalledWith()
    expect(api.getOffer).not.toHaveBeenCalled()
  })

  it('should display admin creation banner when no offererId is given', async () => {
    await renderIndividualOfferWizardRoute(
      store,
      generatePath(
        getIndividualOfferPath({
          step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
          mode: OFFER_WIZARD_MODE.CREATION,
          isCreation: true,
        })
      )
    )
    expect(
      await screen.findByText(
        'Afin de créer une offre en tant qu’administrateur veuillez sélectionner une structure.'
      )
    ).toBeInTheDocument()
    expect(
      screen.queryByRole('heading', { name: 'Type d’offre' })
    ).not.toBeInTheDocument()

    expect(api.getVenues).not.toHaveBeenCalled()
    expect(api.listOfferersNames).not.toHaveBeenCalled()
    expect(api.getCategories).not.toHaveBeenCalled()
    expect(api.getOffer).not.toHaveBeenCalled()
  })

  it('should initialize context with api when a offerId is given', async () => {
    vi.spyOn(api, 'getCategories').mockResolvedValue({
      categories: [
        {
          id: 'A',
          proLabel: 'Category name',
          isSelectable: true,
        },
      ],
      subcategories: [
        {
          id: SubcategoryIdEnum.SEANCE_CINE,
          proLabel: 'Sub category name',
          appLabel: 'Sub category name',
          categoryId: 'A',
          isSelectable: true,
          canBeDuo: true,
          canBeEducational: true,
          canExpire: false,
          conditionalFields: [],
          isDigitalDeposit: false,
          isEvent: true,
          isPhysicalDeposit: true,
          canBeWithdrawable: false,
          onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
          reimbursementRule: '',
        },
      ],
    })
    const offerId = 12
    await renderIndividualOfferWizardRoute(
      store,
      generatePath(
        getIndividualOfferPath({
          step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
          mode: OFFER_WIZARD_MODE.EDITION,
        }),
        { offerId }
      ) +
        '?structure=' +
        offerer.id
    )
    expect(
      await screen.findByRole('heading', { name: 'Modifier l’offre' })
    ).toBeInTheDocument()
    expect(api.getVenues).toHaveBeenCalledWith(
      null, // validated
      true, // activeOfferersOnly,
      offerer.id // offererId
    )
    expect(api.getCategories).toHaveBeenCalledWith()

    expect(api.listOfferersNames).not.toHaveBeenCalled()
    expect(api.getOffer).toHaveBeenCalledWith(offerId)
  })
})
