import {
  screen,
  waitForElementToBeRemoved,
  waitFor,
} from '@testing-library/react'
import React from 'react'
import { generatePath, Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import {
  GetIndividualOfferResponseModel,
  OfferStatus,
  SubcategoryIdEnum,
} from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import { ApiError } from 'apiClient/v2'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferBreadcrumb/constants'
import Notification from 'components/Notification/Notification'
import { CATEGORY_STATUS, OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { getIndividualOfferPath } from 'core/Offers/utils/getIndividualOfferUrl'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import {
  GetIndividualOfferFactory,
  getOfferVenueFactory,
  offererFactory,
} from 'utils/apiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import IndividualOfferWizard from '../IndividualOfferWizard'

vi.mock('core/Notification/constants', () => ({
  NOTIFICATION_TRANSITION_DURATION: 10,
  NOTIFICATION_SHOW_DURATION: 10,
}))

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
    <>
      <Routes>
        <Route
          path="offre/individuelle/:offerId/*"
          element={<IndividualOfferWizard />}
        />
        <Route path="/accueil" element={<>Home Page</>} />
      </Routes>
      <Notification />
    </>,
    { storeOverrides, initialRouterEntries: [url] }
  )

describe('IndividualOfferWisard', () => {
  let store: any

  beforeEach(() => {
    store = {
      user: {
        initialized: true,
        currentUser: {
          isAdmin: false,
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

  it('should display an error when unable to load offer', async () => {
    vi.spyOn(api, 'getOffer').mockRejectedValueOnce(
      new ApiError(
        {} as ApiRequestOptions,
        {
          body: {
            global: ['Une erreur est survenue'],
          },
        } as ApiResult,
        ''
      )
    )
    renderIndividualOfferWizardRoute(
      store,
      generatePath(
        getIndividualOfferPath({
          step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
          mode: OFFER_WIZARD_MODE.CREATION,
        }),
        { offerId: 'OFFER_ID' }
      )
    )

    await waitFor(() => {
      expect(
        screen.getByText(
          /Une erreur est survenue lors de la récupération de votre offre/
        )
      ).toBeInTheDocument()
    })
  })

  it('should display an error when unable to load categories', async () => {
    vi.spyOn(api, 'getCategories').mockRejectedValueOnce(
      new ApiError(
        {} as ApiRequestOptions,
        {
          body: {
            global: ['Une erreur est survenue'],
          },
        } as ApiResult,
        ''
      )
    )
    renderIndividualOfferWizardRoute(
      store,
      generatePath(
        getIndividualOfferPath({
          step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
          mode: OFFER_WIZARD_MODE.CREATION,
          isCreation: true,
        })
      )
    )
    await waitForElementToBeRemoved(() =>
      screen.getByText(/Chargement en cours/)
    )
    await waitFor(() => {
      expect(screen.getByText(GET_DATA_ERROR_MESSAGE)).toBeInTheDocument()
    })
  })

  it('should initialize context with api', async () => {
    renderIndividualOfferWizardRoute(
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
      await screen.findByRole('heading', { name: 'Créer une offre' })
    ).toBeInTheDocument()
    expect(api.listOfferersNames).toHaveBeenCalledWith(
      null, // validated
      null, // validatedForUser
      undefined // offererId
    )
    expect(api.getVenues).toHaveBeenCalledWith(
      null, // validated
      true, // activeOfferersOnly,
      undefined // offererId
    )
    expect(api.getCategories).toHaveBeenCalledWith()
    expect(api.getOffer).not.toHaveBeenCalled()
  })

  it('should initialize context with api when offererId is given in query', async () => {
    renderIndividualOfferWizardRoute(
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
    expect(api.listOfferersNames).toHaveBeenCalledWith(
      null, // validated
      null, // validatedForUser
      undefined // offererId
    )
    expect(api.getVenues).toHaveBeenCalledWith(
      null, // validated
      true, // activeOfferersOnly,
      undefined // offererId, undefinded because we need all the venues
    )
    expect(api.getCategories).toHaveBeenCalledWith()
    expect(api.getOffer).not.toHaveBeenCalled()
  })

  it('should initialize context with api when a offerId is given', async () => {
    vi.spyOn(api, 'getCategories').mockResolvedValueOnce({
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
    renderIndividualOfferWizardRoute(
      store,
      generatePath(
        getIndividualOfferPath({
          step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
          mode: OFFER_WIZARD_MODE.EDITION,
        }),
        { offerId }
      ) + `?structure=${apiOffer.venue.managingOfferer.id}`
    )
    expect(
      await screen.findByRole('heading', { name: 'Modifier l’offre' })
    ).toBeInTheDocument()
    expect(api.listOfferersNames).toHaveBeenCalledWith(
      null, // validated
      null, // validatedForUser
      undefined // offererId
    )
    expect(api.getVenues).toHaveBeenCalledWith(
      null, // validated
      true, // activeOfferersOnly,
      undefined // offererId, undefined because we need all the venues
    )
    expect(api.getCategories).toHaveBeenCalledWith()
    expect(api.getOffer).toHaveBeenCalledWith(offerId)
  })

  describe('stepper', () => {
    it('should render stepper on information page', async () => {
      renderIndividualOfferWizardRoute(
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
        await screen.findByRole('heading', { name: 'Créer une offre' })
      ).toBeInTheDocument()

      const tabInformations = screen.getByText('Détails de l’offre', {
        selector: 'span',
      })
      const tabStocks = screen.getByText('Stock & Prix', {
        selector: 'span',
      })
      const tabSummary = screen.getByText('Récapitulatif', {
        selector: 'span',
      })
      const tabConfirmation = screen.getByText('Confirmation', {
        selector: 'span',
      })

      expect(tabInformations).toBeInTheDocument()
      expect(tabStocks).toBeInTheDocument()
      expect(tabSummary).toBeInTheDocument()
      expect(tabConfirmation).toBeInTheDocument()
    })

    it('should render stepper on summary page in creation', async () => {
      renderIndividualOfferWizardRoute(
        store,
        generatePath(
          getIndividualOfferPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: 'YA' }
        )
      )
      expect(
        await screen.findByRole('heading', { name: /Créer une offre/ })
      ).toBeInTheDocument()

      const tabInformations = screen.getByText('Détails de l’offre', {
        selector: 'span',
      })
      const tabStocks = screen.getByText('Stock & Prix', {
        selector: 'span',
      })
      const tabSummary = screen.getByText('Récapitulatif', {
        selector: 'span',
      })
      const tabConfirmation = screen.getByText('Confirmation', {
        selector: 'span',
      })
      expect(tabInformations).toBeInTheDocument()
      expect(tabStocks).toBeInTheDocument()
      expect(tabSummary).toBeInTheDocument()
      expect(tabConfirmation).toBeInTheDocument()
    })

    it('should not render stepper on summary page in read only mode', async () => {
      renderIndividualOfferWizardRoute(
        store,
        generatePath(
          getIndividualOfferPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.READ_ONLY,
          }),
          { offerId: 'YA' }
        )
      )
      expect(
        await screen.findByRole('heading', { name: /Récapitulatif/ })
      ).toBeInTheDocument()

      const tabInformations = screen.queryByText('Informations', {
        selector: 'span',
      })
      const tabStocks = screen.queryByText('Stock & Prix', {
        selector: 'span',
      })
      const tabSummary = screen.queryByText('Récapitulatif', {
        selector: 'span',
      })
      const tabConfirmation = screen.queryByText('Confirmation', {
        selector: 'span',
      })

      expect(tabInformations).not.toBeInTheDocument()
      expect(tabStocks).not.toBeInTheDocument()
      expect(tabSummary).not.toBeInTheDocument()
      expect(tabConfirmation).not.toBeInTheDocument()
    })
  })
})
