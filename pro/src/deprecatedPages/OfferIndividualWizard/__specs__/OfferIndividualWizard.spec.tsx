import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import React from 'react'
import { generatePath, Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import {
  GetIndividualOfferResponseModel,
  SubcategoryIdEnum,
} from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import { ApiError } from 'apiClient/v2'
import Notification from 'components/Notification/Notification'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import { CATEGORY_STATUS, OFFER_WIZARD_MODE } from 'core/Offers'
import { getOfferIndividualPath } from 'core/Offers/utils/getOfferIndividualUrl'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import {
  GetIndividualOfferFactory,
  getOfferVenueFactory,
  offererFactory,
} from 'utils/apiFactories'
import { dehumanizeId } from 'utils/dehumanize'
import { renderWithProviders } from 'utils/renderWithProviders'

import OfferIndividualWizard from '../OfferIndividualWizard'

jest.mock('core/Notification/constants', () => ({
  NOTIFICATION_TRANSITION_DURATION: 10,
  NOTIFICATION_SHOW_DURATION: 10,
}))

const offerer = offererFactory({ id: 'AM' })
const venue = getOfferVenueFactory(undefined, offerer)
const apiOffer: GetIndividualOfferResponseModel = GetIndividualOfferFactory(
  undefined,
  undefined,
  venue
)

const renderOfferIndividualWizardRoute = (
  storeOverrides: any,
  url = '/offre/v3'
) =>
  renderWithProviders(
    <>
      <Routes>
        <Route
          path="offre/individuelle/:offerId/*"
          element={<OfferIndividualWizard />}
        />
        <Route path="/accueil" element={<>Home Page</>} />
      </Routes>
      <Notification />
    </>,
    { storeOverrides, initialRouterEntries: [url] }
  )

describe('test OfferIndividualWisard', () => {
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
    jest
      .spyOn(api, 'listOfferersNames')
      .mockResolvedValue({ offerersNames: [] })
    jest.spyOn(api, 'getVenues').mockResolvedValue({ venues: [] })
    jest
      .spyOn(api, 'getCategories')
      .mockResolvedValue({ categories: [], subcategories: [] })
    jest.spyOn(api, 'getOffer').mockResolvedValue(apiOffer)
    jest.spyOn(api, 'listOffers').mockResolvedValue([
      {
        id: 'id',
        nonHumanizedId: 1,
        status: 'ACTIVE',
        isActive: true,
        hasBookingLimitDatetimesPassed: false,
        isEducational: false,
        name: 'name',
        isEvent: false,
        venue: {
          name: 'venue',
          offererName: 'offerer',
          isVirtual: false,
          id: 'venueid',
          nonHumanizedId: 1,
          managingOffererId: '',
        },
        stocks: [],
        isEditable: true,
        isShowcase: false,
        isThing: false,
        subcategoryId: SubcategoryIdEnum.VOD,
        venueId: 'venueid',
      },
    ])
  })

  it('should display an error when unable to load offer', async () => {
    jest.spyOn(api, 'getOffer').mockRejectedValue(
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
    renderOfferIndividualWizardRoute(
      store,
      generatePath(
        getOfferIndividualPath({
          step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
          mode: OFFER_WIZARD_MODE.CREATION,
        }),
        { offerId: 'OFFER_ID' }
      )
    )
    await waitForElementToBeRemoved(() =>
      screen.getByText(/Chargement en cours/)
    )
    expect(
      await screen.findByText(
        /Une erreur est survenue lors de la récupération de votre offre/
      )
    ).toBeInTheDocument()
  })

  it('should display an error when unable to load categories', async () => {
    jest.spyOn(api, 'getCategories').mockRejectedValue(
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
    renderOfferIndividualWizardRoute(
      store,
      generatePath(
        getOfferIndividualPath({
          step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
          mode: OFFER_WIZARD_MODE.CREATION,
          isCreation: true,
        })
      )
    )
    await waitForElementToBeRemoved(() =>
      screen.getByText(/Chargement en cours/)
    )
    expect(await screen.findByText(GET_DATA_ERROR_MESSAGE)).toBeInTheDocument()
  })

  it('should initialize context with api', async () => {
    renderOfferIndividualWizardRoute(
      store,
      generatePath(
        getOfferIndividualPath({
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
    renderOfferIndividualWizardRoute(
      store,
      generatePath(
        getOfferIndividualPath({
          step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
          mode: OFFER_WIZARD_MODE.CREATION,
          isCreation: true,
        })
      ) +
        '?structure=' +
        offerer.nonHumanizedId
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
      offerer.nonHumanizedId // offererId
    )
    expect(api.getCategories).toHaveBeenCalledWith()
    expect(api.getOffer).not.toHaveBeenCalled()
  })

  it('should initialize context with api when a offerId is given', async () => {
    jest.spyOn(api, 'getCategories').mockResolvedValue({
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
    renderOfferIndividualWizardRoute(
      store,
      generatePath(
        getOfferIndividualPath({
          step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
          mode: OFFER_WIZARD_MODE.EDITION,
        }),
        { offerId }
      ) + `?structure=${dehumanizeId(apiOffer.venue.managingOfferer.id)}`
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
      dehumanizeId(apiOffer.venue.managingOfferer.id) // offererId
    )
    expect(api.getCategories).toHaveBeenCalledWith()
    expect(api.getOffer).toHaveBeenCalledWith(offerId)
  })

  describe('stepper', () => {
    it('should not render stepper on information page', async () => {
      renderOfferIndividualWizardRoute(
        store,
        generatePath(
          getOfferIndividualPath({
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

    it('should not render stepper on confirmation page', async () => {
      const offerId = 'YA'
      renderOfferIndividualWizardRoute(
        store,
        `/offre/individuelle/${offerId}/confirmation`
      )

      expect(
        await screen.findByRole('heading', { name: 'Modifier l’offre' })
      ).toBeInTheDocument()

      const tabInformations = screen.queryByText('Détails de l’offre', {
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

    it('should render stepper on summary page in creation', async () => {
      renderOfferIndividualWizardRoute(
        store,
        generatePath(
          getOfferIndividualPath({
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

    it('should not render stepper on summary page in edition', async () => {
      renderOfferIndividualWizardRoute(
        store,
        generatePath(
          getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.EDITION,
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
