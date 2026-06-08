import { act, fireEvent, screen, waitFor, within } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { add, addDays, format, set, sub } from 'date-fns'
import { generatePath, Route, Routes } from 'react-router'
import { expect } from 'vitest'

import { api } from '@/apiClient/api'
import {
  ApiError,
  CancelablePromise,
  type GetIndividualOfferResponseModel,
  OfferStatus,
  SimplifiedBankAccountStatus,
  type StockStatsResponseModel,
  SubcategoryIdEnum,
} from '@/apiClient/v1'
import type { ApiRequestOptions } from '@/apiClient/v1/core/ApiRequestOptions'
import type { ApiResult } from '@/apiClient/v1/core/ApiResult'
import { DisplayableActivity } from '@/apiClient/v1/new'
import * as useAnalytics from '@/app/App/analytics/firebase'
import {
  IndividualOfferContext,
  type IndividualOfferContextValues,
} from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferPath } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import { FORMAT_ISO_DATE_ONLY } from '@/commons/utils/date'
import { getLocationResponseModelV2 } from '@/commons/utils/factories/commonOffersApiFactories'
import {
  getIndividualOfferFactory,
  getOfferManagingOffererFactory,
  getOfferVenueFactory,
  getStocksResponseFactory,
  subcategoryFactory,
} from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import {
  type RenderComponentFunction,
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'
import { SnackBarContainer } from '@/components/SnackBarContainer/SnackBarContainer'
import {
  MOCKED_CATEGORIES,
  MOCKED_CATEGORY,
  MOCKED_SUBCATEGORIES,
  MOCKED_SUBCATEGORY,
} from '@/pages/IndividualOffer/commons/__mocks__/constants'

import { IndividualOfferSummaryScreen } from './IndividualOfferSummaryScreen'

const LABELS = {
  publicationModeNowRadio: /Publier maintenant/,
  publicationModeLaterRadio: /Publier plus tard/,
  publicationDateInput: 'Date *',
  submitInstantOfferButton: 'Publier l’offre',
  submitScheduledOfferButton: 'Programmer l’offre',
}

const ERROR_MESSAGES = {
  publicationDateIsRequired: /Veuillez sélectionner une date de publication/,
  publicationTimeIsRequired: /Veuillez sélectionner une heure de publication/,
  publicationDateMustBeInFuture: /Veuillez indiquer une date dans le futur/,
  publicationDateMustBeWithinTwoYears:
    /Veuillez indiquer une date dans les 2 ans à venir/,
}

const mockLogEvent = vi.fn()

type ExtraParams = {
  selectedPartnerVenueBankAccountStatus?: SimplifiedBankAccountStatus | null
  selectedPartnerVenueHasNonFreeOffers?: boolean
}

const renderIndividualOfferSummaryScreen: RenderComponentFunction<
  void,
  IndividualOfferContextValues,
  ExtraParams
> = (params) => {
  const offer =
    params.contextValues?.offer ??
    getIndividualOfferFactory({
      id: 1,
      audioDisabilityCompliant: false,
      bookingEmail: 'booking@example.com',
      description: 'ma description',
      isDigital: true,
      isEvent: true,
      lastProvider: {
        name: 'Ciné Office',
      },
      mentalDisabilityCompliant: false,
      motorDisabilityCompliant: false,
      name: 'mon offre',
      subcategoryId: MOCKED_SUBCATEGORY.EVENT_ONLINE.id,
      status: OfferStatus.PUBLISHED,
      url: 'https://offer-url.example.com',
      venue: getOfferVenueFactory({
        name: 'ma venue',
        publicName: 'Nom public de la structure',
        managingOfferer: getOfferManagingOffererFactory({
          name: "Nom de l'entité",
        }),
      }),
      visualDisabilityCompliant: false,
      withdrawalDetails: 'détails de retrait',
    })
  const contextValues: IndividualOfferContextValues = {
    categories: MOCKED_CATEGORIES,
    hasPublishedOfferWithSameEan: false,
    isEvent: false,
    offer,
    offerId: offer.id,
    setIsControlledEvent: vi.fn(),
    subCategories: MOCKED_SUBCATEGORIES,
    ...params.contextValues,
  }

  assertOrFrontendError(
    params.path,
    '`path` is required to render the component.'
  )
  const path = params.path

  const options: RenderWithProvidersOptions = {
    initialRouterEntries: [path],
    user: sharedCurrentUserFactory(),
    storeOverrides: {
      user: {
        currentUser: sharedCurrentUserFactory(),
        selectedPartnerVenue: makeGetVenueResponseModel({
          id: offer.venue.id,
          bankAccountStatus:
            params.selectedPartnerVenueBankAccountStatus === undefined
              ? SimplifiedBankAccountStatus.VALID
              : params.selectedPartnerVenueBankAccountStatus,
          hasNonFreeOffers:
            params.selectedPartnerVenueHasNonFreeOffers ?? false,
        }),
      },
    },
    ...params.options,
  }

  return renderWithProviders(
    <>
      <IndividualOfferContext.Provider value={contextValues}>
        <Routes>
          <Route
            path={getIndividualOfferPath({
              step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY,
              mode: OFFER_WIZARD_MODE.READ_ONLY,
            })}
            element={<IndividualOfferSummaryScreen offer={offer} />}
          />
          <Route
            path={getIndividualOfferPath({
              step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY,
              mode: OFFER_WIZARD_MODE.CREATION,
            })}
            element={<IndividualOfferSummaryScreen offer={offer} />}
          />
          <Route
            path={`/onboarding${getIndividualOfferPath({
              step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY,
              mode: OFFER_WIZARD_MODE.CREATION,
            })}`}
            element={<IndividualOfferSummaryScreen offer={offer} />}
          />
          <Route
            path={getIndividualOfferPath({
              step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.CONFIRMATION,
              mode: OFFER_WIZARD_MODE.CREATION,
            })}
            element={<div>Confirmation page: creation</div>}
          />
        </Routes>
      </IndividualOfferContext.Provider>
      <SnackBarContainer />
    </>,
    options
  )
}

const stocksStats: StockStatsResponseModel = {
  stockCount: 1,
  remainingQuantity: 637,
  oldestStock: '2021-01-01T00:00:00+01:00',
  newestStock: '2021-01-01T00:00:00+01:00',
}

describe('IndividualOfferSummaryScreen', () => {
  const offerBase = getIndividualOfferFactory({
    audioDisabilityCompliant: false,
    bookingEmail: 'booking@example.com',
    description: 'ma description',
    isDigital: true,
    isEvent: true,
    lastProvider: {
      name: 'Ciné Office',
    },
    mentalDisabilityCompliant: false,
    motorDisabilityCompliant: false,
    name: 'mon offre',
    subcategoryId: MOCKED_SUBCATEGORY.EVENT_ONLINE.id,
    status: OfferStatus.PUBLISHED,
    url: 'https://offer-url.example.com',
    venue: getOfferVenueFactory({
      name: 'ma venue',
      publicName: 'Nom public de la structure',
      managingOfferer: getOfferManagingOffererFactory({
        name: "Nom de l'entité",
      }),
    }),
    visualDisabilityCompliant: false,
    withdrawalDetails: 'détails de retrait',
  })
  const contextValuesBase: IndividualOfferContextValues = {
    categories: MOCKED_CATEGORIES,
    hasPublishedOfferWithSameEan: false,
    isEvent: false,
    offer: offerBase,
    offerId: offerBase.id,
    setIsControlledEvent: vi.fn(),
    subCategories: MOCKED_SUBCATEGORIES,
  }

  beforeEach(() => {
    const musicTypes = [
      {
        gtl_id: '07000000',
        label: 'Metal',
        canBeEvent: true,
      },
      {
        gtl_id: '02000000',
        label: 'JAZZ / BLUES',
        canBeEvent: true,
      },
      {
        gtl_id: '03000000',
        label: 'Bandes Originales',
        canBeEvent: false,
      },
    ]

    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))

    vi.spyOn(api, 'patchPublishOffer').mockResolvedValue(
      getIndividualOfferFactory()
    )
    vi.spyOn(api, 'getMusicTypes').mockResolvedValue(musicTypes)
    vi.spyOn(api, 'getStocksStats').mockResolvedValue(stocksStats)
    vi.spyOn(api, 'getStocks').mockResolvedValue(
      getStocksResponseFactory({ totalStockCount: 0, stocks: [] })
    )
    vi.spyOn(api, 'getVenue').mockResolvedValue(
      makeGetVenueResponseModel({ id: 1 })
    )
  })

  const expectOfferFields = async () => {
    expect(await screen.findByText('Description')).toBeInTheDocument()
    expect(screen.getByText('Type d’offre')).toBeInTheDocument()
    expect(screen.getByText('Modalités d’accessibilité')).toBeInTheDocument()
    expect(
      screen.getByText('Notifications des réservations')
    ).toBeInTheDocument()
    expect(screen.getByText('Aperçu dans l’app')).toBeInTheDocument()

    expect(screen.getByText(MOCKED_CATEGORY.A.proLabel)).toBeInTheDocument()
    expect(
      screen.getByText(MOCKED_SUBCATEGORY.EVENT_ONLINE.proLabel)
    ).toBeInTheDocument()
    expect(screen.getByText('détails de retrait')).toBeInTheDocument()
    expect(screen.getByText('Non accessible')).toBeInTheDocument()
    expect(screen.getByText('booking@example.com')).toBeInTheDocument()
    expect(screen.getAllByText('mon offre')).toHaveLength(2)
    expect(screen.getAllByText('ma description')).toHaveLength(2)
  }

  describe('when mode = "CREATION"', () => {
    const path = generatePath(
      getIndividualOfferPath({
        step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY,
        mode: OFFER_WIZARD_MODE.CREATION,
      }),
      { offerId: '1' }
    )

    const draftOfferBase = {
      ...offerBase,
      status: OfferStatus.DRAFT,
    }

    const contextValuesWithDraftOffer: IndividualOfferContextValues = {
      ...contextValuesBase,
      offer: draftOfferBase,
    }

    it('should render component with informations', async () => {
      const contextValues = { offer: draftOfferBase }

      renderIndividualOfferSummaryScreen({ contextValues, path })

      await expectOfferFields()
      expect(screen.queryByText('Visualiser dans l’app')).toBeInTheDocument()
    })

    it('should render a media section', async () => {
      const contextValues = { offer: draftOfferBase }

      renderIndividualOfferSummaryScreen({ contextValues, path })

      await waitFor(() => {
        expect(
          screen.getByRole('heading', { name: 'Image et vidéo' })
        ).toBeInTheDocument()
      })
    })

    it('should render component with new sections', async () => {
      renderIndividualOfferSummaryScreen({
        contextValues: { offer: draftOfferBase },
        path,
      })

      expect(
        await screen.findByText('À propos de votre offre')
      ).toBeInTheDocument()
    })

    it('should render component with right buttons', async () => {
      const contextValues = { offer: draftOfferBase }

      renderIndividualOfferSummaryScreen({ contextValues, path })

      await waitFor(() => {
        expect(screen.getByText('Retour')).toBeInTheDocument()
      })
      expect(
        screen.getByText('Sauvegarder le brouillon et quitter')
      ).toBeInTheDocument()
      expect(
        screen.getByRole('button', { name: /Publier l’offre/ })
      ).toBeInTheDocument()
    })

    it('should link to creation confirmation page', async () => {
      const contextValues = { offer: draftOfferBase }

      renderIndividualOfferSummaryScreen({ contextValues, path })

      await userEvent.click(
        screen.getByRole('button', { name: /Publier l’offre/ })
      )

      expect(
        await screen.findByText(/Confirmation page: creation/)
      ).toBeInTheDocument()
    })

    it('should disabled publish button link during submit', async () => {
      const contextValues = { offer: draftOfferBase }

      renderIndividualOfferSummaryScreen({ contextValues, path })

      const pageTitle = await screen.findByRole('heading', {
        name: /Description/,
      })
      const buttonPublish = screen.getByRole('button', {
        name: /Publier l’offre/,
      })
      expect(buttonPublish).not.toBeDisabled()

      const mockResponse =
        new CancelablePromise<GetIndividualOfferResponseModel>((resolve) =>
          setTimeout(() => {
            resolve(getIndividualOfferFactory())
          }, 200)
        )
      vi.spyOn(api, 'patchPublishOffer').mockImplementationOnce(
        () => mockResponse
      )
      await userEvent.click(buttonPublish)
      expect(api.patchPublishOffer).toHaveBeenCalled()
      expect(buttonPublish).toBeDisabled()
      await waitFor(() => expect(pageTitle).not.toBeInTheDocument())
      expect(
        screen.getByText('Confirmation page: creation')
      ).toBeInTheDocument()
    })

    it('should allow to publish offer later', async () => {
      // Mock current date to avoid DST issues
      vi.setSystemTime(new Date('2024-01-15T12:00:00.000Z'))

      const contextValues = { offer: draftOfferBase }

      renderIndividualOfferSummaryScreen({ contextValues, path })

      await userEvent.click(screen.getByLabelText(/Publier plus tard/))

      await userEvent.click(
        screen.getByRole('button', { name: 'Programmer l’offre' })
      )

      expect(
        await screen.findByText('Veuillez sélectionner une date de publication')
      ).toBeInTheDocument()
      expect(
        screen.getByText('Veuillez sélectionner une heure de publication')
      ).toBeInTheDocument()
      expect(
        screen.queryByText(/Confirmation page: creation/)
      ).not.toBeInTheDocument()

      const publicationDate = format(
        addDays(new Date(), 1),
        FORMAT_ISO_DATE_ONLY
      )

      await userEvent.type(screen.getByLabelText('Date *'), publicationDate)
      await userEvent.selectOptions(screen.getByLabelText(/Heure/), '11:00')

      await userEvent.click(
        screen.getByRole('button', { name: 'Programmer l’offre' })
      )

      expect(
        await screen.findByText(/Confirmation page: creation/)
      ).toBeInTheDocument()
      expect(api.patchPublishOffer).toHaveBeenCalledWith({
        id: 1,
        publicationDatetime: `${publicationDate}T10:00:00Z`,
      })

      // Clean up the mocked time
      vi.useRealTimers()
    })

    it('should allow to maker offer bookable later', async () => {
      // Mock current date to avoid DST issues
      vi.setSystemTime(new Date('2024-01-15T12:00:00.000Z'))

      const contextValues = {
        offer: draftOfferBase,
      }

      renderIndividualOfferSummaryScreen({ contextValues, path })

      await userEvent.click(
        screen.getByLabelText(/Rendre réservable plus tard/)
      )

      await userEvent.click(
        screen.getByRole('button', { name: 'Publier l’offre' })
      )

      expect(
        await screen.findByText(
          'Veuillez sélectionner une date de réservabilité'
        )
      ).toBeInTheDocument()
      expect(
        screen.getByText('Veuillez sélectionner une heure de réservabilité')
      ).toBeInTheDocument()
      expect(
        screen.queryByText(/Confirmation page: creation/)
      ).not.toBeInTheDocument()

      const bookingAllowedDate = format(
        addDays(new Date(), 1),
        FORMAT_ISO_DATE_ONLY
      )

      await userEvent.type(screen.getByLabelText('Date *'), bookingAllowedDate)
      await userEvent.selectOptions(screen.getByLabelText(/Heure/), '11:00')

      await userEvent.click(
        screen.getByRole('button', { name: 'Publier l’offre' })
      )

      expect(
        await screen.findByText(/Confirmation page: creation/)
      ).toBeInTheDocument()
      expect(api.patchPublishOffer).toHaveBeenCalledWith({
        id: 1,
        bookingAllowedDatetime: `${bookingAllowedDate}T10:00:00Z`,
      })

      // Clean up the mocked time
      vi.useRealTimers()
    })

    it('should display notification on api error', async () => {
      const contextValues = { offer: draftOfferBase }

      renderIndividualOfferSummaryScreen({ contextValues, path })

      vi.spyOn(api, 'patchPublishOffer').mockRejectedValue(
        new ApiError(
          {} as ApiRequestOptions,
          {
            status: 400,
            body: {},
          } as ApiResult,
          ''
        )
      )

      await userEvent.click(
        screen.getByRole('button', {
          name: /Publier l’offre/,
        })
      )
      expect(
        await screen.findByText('Une erreur s’est produite, veuillez réessayer')
      ).toBeInTheDocument()
    })

    it('should display redirect modal when the partner venue has no bank account and the offer is non-free', async () => {
      vi.spyOn(api, 'patchPublishOffer').mockResolvedValue(
        getIndividualOfferFactory({
          isNonFreeOffer: true,
        })
      )
      const expectedOffererId = 2

      const venueId = 1
      const contextValues = {
        offer: {
          ...offerBase,
          venue: getOfferVenueFactory({
            id: venueId,
            managingOfferer: getOfferManagingOffererFactory({
              id: expectedOffererId,
            }),
          }),
        },
      }

      renderIndividualOfferSummaryScreen({
        contextValues,
        path,
        selectedPartnerVenueBankAccountStatus: null,
      })

      await userEvent.click(
        screen.getByRole('button', { name: /Publier l’offre/ })
      )

      await waitFor(() => {
        expect(
          screen.getByText('Félicitations, vous avez créé votre offre !')
        ).toBeInTheDocument()
      })
      expect(
        screen.getByRole('button', {
          name: /Vous allez être redirigé vers la page d'administration de vos informations bancaires/,
        })
      ).toBeInTheDocument()
    })

    it('should not display redirect modal when the partner venue already has a bank account', async () => {
      vi.spyOn(api, 'patchPublishOffer').mockResolvedValue(
        getIndividualOfferFactory({ isNonFreeOffer: true })
      )

      const contextValues = { offer: draftOfferBase }

      renderIndividualOfferSummaryScreen({
        contextValues,
        path,
        selectedPartnerVenueBankAccountStatus:
          SimplifiedBankAccountStatus.VALID,
      })

      await userEvent.click(
        screen.getByRole('button', { name: /Publier l’offre/ })
      )

      expect(
        screen.queryByText('Félicitations, vous avez créé votre offre !')
      ).not.toBeInTheDocument()
    })

    it('should not display redirect modal if offer is free', async () => {
      vi.spyOn(api, 'patchPublishOffer').mockResolvedValue(
        getIndividualOfferFactory({ isNonFreeOffer: false })
      )

      const contextValues = { offer: draftOfferBase }

      renderIndividualOfferSummaryScreen({
        contextValues,
        path,
        selectedPartnerVenueBankAccountStatus: null,
      })

      await userEvent.click(
        screen.getByRole('button', { name: /Publier l’offre/ })
      )

      expect(
        screen.queryByText('Félicitations, vous avez créé votre offre !')
      ).not.toBeInTheDocument()
    })

    it('should not display redirect modal if the partner venue already has non-free offers', async () => {
      vi.spyOn(api, 'patchPublishOffer').mockResolvedValue(
        getIndividualOfferFactory({ isNonFreeOffer: true })
      )

      const contextValues = { offer: draftOfferBase }

      renderIndividualOfferSummaryScreen({
        contextValues,
        path,
        selectedPartnerVenueBankAccountStatus: null,
        selectedPartnerVenueHasNonFreeOffers: true,
      })

      await userEvent.click(
        screen.getByRole('button', { name: /Publier l’offre/ })
      )

      expect(
        screen.queryByText('Félicitations, vous avez créé votre offre !')
      ).not.toBeInTheDocument()
    })

    it('should display redirect modal in onboarding mode regardless of bank account or non-free offers', async () => {
      vi.spyOn(api, 'patchPublishOffer').mockResolvedValue(
        getIndividualOfferFactory({ isNonFreeOffer: false })
      )

      const onboardingPath = generatePath(
        `/onboarding${getIndividualOfferPath({
          step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY,
          mode: OFFER_WIZARD_MODE.CREATION,
        })}`,
        { offerId: '1' }
      )

      const contextValues = { offer: draftOfferBase }

      renderIndividualOfferSummaryScreen({
        contextValues,
        path: onboardingPath,
        selectedPartnerVenueBankAccountStatus:
          SimplifiedBankAccountStatus.VALID,
        selectedPartnerVenueHasNonFreeOffers: true,
      })

      await userEvent.click(
        screen.getByRole('button', { name: /Publier l’offre/ })
      )

      expect(
        await screen.findByText('Félicitations, vous avez créé votre offre !')
      ).toBeInTheDocument()
    })

    it('should render component with new sections and right address data', async () => {
      const contextValues = {
        offer: {
          ...offerBase,
          location: {
            ...getLocationResponseModelV2({
              label: 'mon adresse',
              city: 'ma ville',
              street: 'ma street',
              postalCode: '1',
            }),
          },
          isDigital: false,
          subcategoryId: MOCKED_SUBCATEGORY.EVENT_OFFLINE.id,
          url: null,
        },
      }

      renderIndividualOfferSummaryScreen({ contextValues, path })

      expect(await screen.findByText(/Structure/)).toBeInTheDocument()
      expect(
        await screen.findByText('Localisation de l’offre')
      ).toBeInTheDocument()

      // Present without the colon « : » in the <VenueDetails /> component
      expect(screen.getByText('Intitulé')).toBeInTheDocument()
      expect(screen.getByText('Adresse')).toBeInTheDocument()

      // Present with the colon « : » in the <SummaryScreen /> component
      expect(screen.getByText('Intitulé :')).toBeInTheDocument()
      expect(screen.getByText('Adresse :')).toBeInTheDocument()

      // Both present in <VenueDetails /> and <SummaryScreen /> components
      expect(screen.getAllByText('mon adresse')).toHaveLength(2)
      expect(screen.getAllByText('ma street 1 ma ville')).toHaveLength(2)
    })

    // TODO (igabriele, 2025-08-08): Is this case even possible?
    it('should render component with new sections and empty address data', async () => {
      contextValuesWithDraftOffer.offer = getIndividualOfferFactory({
        isEvent: true,
        location: undefined,
      })
      const contextValues = {
        offer: {
          ...offerBase,
          address: null,
          isDigital: false,
          subcategoryId: MOCKED_SUBCATEGORY.EVENT_OFFLINE.id,
        },
      }

      renderIndividualOfferSummaryScreen({ contextValues, path })

      expect(await screen.findByText(/Structure/)).toBeInTheDocument()
      expect(
        await screen.findByText('Localisation de l’offre')
      ).toBeInTheDocument()

      expect(
        within(screen.getByTestId('localisation-offer-details')).getAllByText(
          '-'
        )
      ).toHaveLength(2)
    })

    it('should display pre publishing banner in creation', async () => {
      const contextValues = { offer: draftOfferBase }

      renderIndividualOfferSummaryScreen({ contextValues, path })

      expect(
        await screen.findByText('Vous y êtes presque !')
      ).toBeInTheDocument()
    })

    it('should display a notification when saving as draft', async () => {
      const contextValues = { offer: draftOfferBase }

      renderIndividualOfferSummaryScreen({ contextValues, path })

      await userEvent.click(
        screen.getByText('Sauvegarder le brouillon et quitter')
      )
      expect(
        screen.getByText('Brouillon sauvegardé dans la liste des offres')
      ).toBeInTheDocument()
    })

    const inOneMonth = set(add(new Date(), { months: 1 }), {
      hours: 10,
      minutes: 0,
    })

    it("should validate publication date and time when it's a scheduled publication", async () => {
      vi.spyOn(api, 'patchPublishOffer').mockResolvedValue(
        getIndividualOfferFactory()
      )

      const contextValues = { offer: draftOfferBase }

      renderIndividualOfferSummaryScreen({ contextValues, path })

      await userEvent.click(
        screen.getByLabelText(LABELS.publicationModeLaterRadio)
      )
      await userEvent.click(
        screen.getByRole('button', { name: LABELS.submitScheduledOfferButton })
      )

      expect(
        await screen.findByText(ERROR_MESSAGES.publicationDateIsRequired)
      ).toBeVisible()
      expect(
        await screen.findByText(ERROR_MESSAGES.publicationTimeIsRequired)
      ).toBeVisible()

      const publicationDateInput = screen.getByLabelText(
        LABELS.publicationDateInput
      )
      const publicationTimeSelect = screen.getByLabelText(/Heure/)

      await userEvent.type(
        publicationDateInput,
        format(inOneMonth, 'yyyy-MM-dd')
      )

      expect(
        screen.queryByText(ERROR_MESSAGES.publicationDateIsRequired)
      ).not.toBeInTheDocument()
      expect(
        screen.queryByText(ERROR_MESSAGES.publicationDateMustBeInFuture)
      ).not.toBeInTheDocument()
      expect(
        screen.queryByText(ERROR_MESSAGES.publicationTimeIsRequired)
      ).toBeVisible()

      await userEvent.selectOptions(
        publicationTimeSelect,
        format(inOneMonth, 'HH:mm')
      )

      expect(
        screen.queryByTestId('error-publicationDate')
      ).not.toBeInTheDocument()

      await userEvent.click(
        screen.getByRole('button', { name: LABELS.submitScheduledOfferButton })
      )

      expect(api.patchPublishOffer).toHaveBeenCalledWith({
        id: 1,
        publicationDatetime: expect.any(String),
        bookingAllowedDatetime: undefined,
      })
    })

    it("should require publication date to be in the future when it's a scheduled publication", async () => {
      vi.spyOn(api, 'patchPublishOffer').mockResolvedValue(
        getIndividualOfferFactory()
      )

      const contextValues = { offer: draftOfferBase }

      renderIndividualOfferSummaryScreen({ contextValues, path })

      await userEvent.click(
        screen.getByLabelText(LABELS.publicationModeLaterRadio)
      )

      const publicationDateInput = screen.getByLabelText(
        LABELS.publicationDateInput
      )
      const publicationTimeSelect = screen.getByLabelText(/Heure/)

      const yesterday = set(sub(new Date(), { days: 1 }), {
        hours: 10,
        minutes: 0,
      })
      await userEvent.type(
        publicationDateInput,
        format(yesterday, 'yyyy-MM-dd')
      )
      await userEvent.selectOptions(
        publicationTimeSelect,
        format(yesterday, 'HH:mm')
      )

      expect(
        await screen.findByText(ERROR_MESSAGES.publicationDateMustBeInFuture)
      ).toBeVisible()

      await userEvent.clear(publicationDateInput)
      await userEvent.type(
        publicationDateInput,
        format(inOneMonth, 'yyyy-MM-dd')
      )

      expect(
        screen.queryByTestId('error-publicationDate')
      ).not.toBeInTheDocument()

      await userEvent.click(
        screen.getByRole('button', { name: LABELS.submitScheduledOfferButton })
      )

      expect(api.patchPublishOffer).toHaveBeenCalledWith({
        id: 1,
        publicationDatetime: expect.any(String),
        bookingAllowedDatetime: undefined,
      })
    })

    it('should show the cultural outreach row when FF is enabled and venue activity is MUSEUM', async () => {
      renderIndividualOfferSummaryScreen({
        contextValues: {
          offer: { ...offerBase, hasCulturalOutreachClaim: true },
        },
        path,
        options: {
          features: ['WIP_ENABLE_CULTURAL_OUTREACH'],
          storeOverrides: {
            user: {
              currentUser: sharedCurrentUserFactory(),
              selectedPartnerVenue: makeGetVenueResponseModel({
                id: offerBase.venue.id,
                activity: DisplayableActivity.MUSEUM,
              }),
            },
          },
        },
      })

      expect(
        await screen.findByText('Inclut une action de médiation spécifique :')
      ).toBeInTheDocument()
      expect(screen.getByText('Oui')).toBeInTheDocument()
    })

    it('should NOT show the cultural outreach row when FF is disabled', async () => {
      renderIndividualOfferSummaryScreen({
        contextValues: {
          offer: { ...offerBase, hasCulturalOutreachClaim: true },
        },
        path,
        options: {
          storeOverrides: {
            user: {
              currentUser: sharedCurrentUserFactory(),
              selectedPartnerVenue: makeGetVenueResponseModel({
                id: offerBase.venue.id,
                activity: DisplayableActivity.MUSEUM,
              }),
            },
          },
        },
      })

      await screen.findByText('Description')
      expect(
        screen.queryByText('Inclut une action de médiation spécifique :')
      ).not.toBeInTheDocument()
    })

    it('should NOT show the cultural outreach row when activity is not allowed', async () => {
      renderIndividualOfferSummaryScreen({
        contextValues: {
          offer: { ...offerBase, hasCulturalOutreachClaim: true },
        },
        path,
        options: {
          features: ['WIP_ENABLE_CULTURAL_OUTREACH'],
          storeOverrides: {
            user: {
              currentUser: sharedCurrentUserFactory(),
              selectedPartnerVenue: makeGetVenueResponseModel({
                id: offerBase.venue.id,
                activity: DisplayableActivity.RECORD_STORE,
              }),
            },
          },
        },
      })

      await screen.findByText('Description')
      expect(
        screen.queryByText('Inclut une action de médiation spécifique :')
      ).not.toBeInTheDocument()
    })

    it('should display booking contact when set on the offer', async () => {
      const contextValues = {
        offer: {
          ...draftOfferBase,
          bookingContact: 'contact@example.com',
        },
      }

      renderIndividualOfferSummaryScreen({ contextValues, path })

      expect(await screen.findByText('contact@example.com')).toBeInTheDocument()
    })

    it('should display music genre and show type rows when subcategory includes them', async () => {
      const customSubcategory = subcategoryFactory({
        id: SubcategoryIdEnum.CONCERT,
        categoryId: MOCKED_CATEGORY.A.id,
        conditionalFields: ['musicType', 'showType'],
      })
      const contextValues = {
        offer: {
          ...draftOfferBase,
          subcategoryId: SubcategoryIdEnum.CONCERT,
          extraData: { gtl_id: '07000000' },
        },
        subCategories: [customSubcategory],
      }

      renderIndividualOfferSummaryScreen({ contextValues, path })

      expect(await screen.findByText(/Genre musical/)).toBeInTheDocument()
      expect(screen.getByText(/Type de spectacle/)).toBeInTheDocument()
      expect(await screen.findByText('Metal')).toBeInTheDocument()
    })

    it("should require publication date to be within two years when it's a scheduled publication", async () => {
      vi.spyOn(api, 'patchPublishOffer').mockResolvedValue(
        getIndividualOfferFactory()
      )

      const contextValues = { offer: draftOfferBase }

      renderIndividualOfferSummaryScreen({ contextValues, path })

      await userEvent.click(
        screen.getByLabelText(LABELS.publicationModeLaterRadio)
      )

      const publicationDateInput = screen.getByLabelText(
        LABELS.publicationDateInput
      )
      const publicationTimeSelect = screen.getByLabelText(/Heure/)

      const inMoreThanTwoYears = set(add(new Date(), { months: 25 }), {
        hours: 10,
        minutes: 0,
      })
      await userEvent.type(
        publicationDateInput,
        format(inMoreThanTwoYears, 'yyyy-MM-dd')
      )
      await userEvent.selectOptions(
        publicationTimeSelect,
        format(inMoreThanTwoYears, 'HH:mm')
      )

      expect(
        await screen.findByText(
          ERROR_MESSAGES.publicationDateMustBeWithinTwoYears
        )
      ).toBeVisible()

      await act(() =>
        fireEvent.input(publicationDateInput, {
          target: {
            value: format(inOneMonth, 'yyyy-MM-dd'),
          },
        })
      )

      expect(
        screen.queryByTestId('error-publicationDate')
      ).not.toBeInTheDocument()

      await userEvent.click(
        screen.getByRole('button', { name: LABELS.submitScheduledOfferButton })
      )

      expect(api.patchPublishOffer).toHaveBeenCalledWith({
        id: 1,
        publicationDatetime: expect.any(String),
        bookingAllowedDatetime: undefined,
      })
    })
  })
})
