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
import { routesIndividualOfferWizard } from 'app/AppRouter/subroutesIndividualOfferWizardMap'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import Notification from 'components/Notification/Notification'
import { CATEGORY_STATUS, OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { getIndividualOfferPath } from 'core/Offers/utils/getIndividualOfferUrl'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import {
  GetIndividualOfferFactory,
  offererFactory,
  offerVenueFactory,
} from 'utils/apiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { IndividualOfferWizard } from '../IndividualOfferWizard'

const offerer = offererFactory({ id: 12 })
const venue = offerVenueFactory(undefined, offerer)
const apiOffer: GetIndividualOfferResponseModel = GetIndividualOfferFactory({
  venue,
})

const renderIndividualOfferWizardRoute = (
  storeOverrides: any,
  url = '/offre/v3'
) =>
  renderWithProviders(
    <>
      <Routes>
        <Route
          path="offre/individuelle/:offerId"
          element={<IndividualOfferWizard />}
        >
          {routesIndividualOfferWizard.map((route) => (
            <Route key={route.path} path={route.path} element={route.element} />
          ))}
        </Route>
        <Route path="/accueil" element={<>Home Page</>} />
      </Routes>
      <Notification />
    </>,
    { storeOverrides, initialRouterEntries: [url] }
  )

describe('IndividualOfferWizard', () => {
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
        selector: 'button',
      })
      const tabStocks = screen.queryByText('Stock & Prix', {
        selector: 'button',
      })
      const tabSummary = screen.queryByText('Récapitulatif', {
        selector: 'button',
      })
      const tabConfirmation = screen.queryByText('Confirmation', {
        selector: 'button',
      })

      expect(tabInformations).not.toBeInTheDocument()
      expect(tabStocks).not.toBeInTheDocument()
      expect(tabSummary).not.toBeInTheDocument()
      expect(tabConfirmation).not.toBeInTheDocument()
    })
  })
})
