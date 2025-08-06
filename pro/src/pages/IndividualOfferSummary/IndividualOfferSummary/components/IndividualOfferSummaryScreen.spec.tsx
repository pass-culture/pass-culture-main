import { act, fireEvent, screen, waitFor, within } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { add, addDays, format, set, sub } from 'date-fns'
import { generatePath, Route, Routes } from 'react-router'
import { expect } from 'vitest'

import { api } from '@/apiClient/api'
import {
  ApiError,
  CancelablePromise,
  GetIndividualOfferResponseModel,
  GetMusicTypesResponse,
  OfferStatus,
  SubcategoryIdEnum,
} from '@/apiClient/v1'
import { ApiRequestOptions } from '@/apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from '@/apiClient/v1/core/ApiResult'
import * as useAnalytics from '@/app/App/analytics/firebase'
import {
  IndividualOfferContext,
  IndividualOfferContextValues,
} from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import {
  CATEGORY_STATUS,
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferPath } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { FORMAT_ISO_DATE_ONLY } from '@/commons/utils/date'
import { getAddressResponseIsLinkedToVenueModelFactory } from '@/commons/utils/factories/commonOffersApiFactories'
import {
  categoryFactory,
  defaultGetOffererResponseModel,
  getIndividualOfferFactory,
  getOfferManagingOffererFactory,
  getOfferVenueFactory,
  individualOfferContextValuesFactory,
  subcategoryFactory,
  venueListItemFactory,
} from '@/commons/utils/factories/individualApiFactories'
import {
  currentOffererFactory,
  sharedCurrentUserFactory,
} from '@/commons/utils/factories/storeFactories'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'
import { Notification } from '@/components/Notification/Notification'

import { IndividualOfferSummaryScreen } from './IndividualOfferSummaryScreen'

// vi.mock('@/apiClient/api', () => ({
//   api: {
//     getMusicTypes: vi.fn(),
//     getOfferer: vi.fn(),
//     patchPublishOffer: vi.fn(),
//   },
// }))

const LABELS = {
  publicationModeNowRadio: /Publier maintenant/,
  publicationModeLaterRadio: /Publier plus tard/,
  publicationDateInput: 'Date *',
  publicationTimeSelect: 'Heure *',
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

const renderIndividualOfferSummaryScreen = ({
  contextValue = {},
  mode = OFFER_WIZARD_MODE.READ_ONLY,
  options,
  path = getIndividualOfferPath({
    step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY,
    mode,
  }),
}: Partial<{
  contextValue: Partial<IndividualOfferContextValues>
  mode: OFFER_WIZARD_MODE
  options: RenderWithProvidersOptions
  path: string
  url: string
}>) => {
  const controlledContextValue =
    individualOfferContextValuesFactory(contextValue)

  return renderWithProviders(
    <>
      <IndividualOfferContext.Provider value={controlledContextValue}>
        <Routes>
          <Route
            path={getIndividualOfferPath({
              step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY,
              mode: OFFER_WIZARD_MODE.READ_ONLY,
            })}
            element={<IndividualOfferSummaryScreen />}
          />
          <Route
            path={getIndividualOfferPath({
              step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY,
              mode: OFFER_WIZARD_MODE.CREATION,
            })}
            element={<IndividualOfferSummaryScreen />}
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
      <Notification />
    </>,
    { initialRouterEntries: [path], ...options }
  )
}

const categories = [categoryFactory({ id: 'A' })]

const subCategories = [
  subcategoryFactory({
    id: String(SubcategoryIdEnum.CONCERT),
    categoryId: 'A',
  }),
  subcategoryFactory({ categoryId: 'A' }),
]

describe('IndividualOfferSummaryScreen', () => {
  let customContext: Partial<IndividualOfferContextValues>
  let musicTypes: GetMusicTypesResponse
  beforeEach(() => {
    musicTypes = [
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
    customContext = {
      offer: getIndividualOfferFactory({
        isEvent: false,
        name: 'mon offre',
        lastProvider: {
          name: 'Ciné Office',
        },
        motorDisabilityCompliant: false,
        mentalDisabilityCompliant: false,
        audioDisabilityCompliant: false,
        visualDisabilityCompliant: false,
        description: 'ma description',
        subcategoryId: SubcategoryIdEnum.CONCERT,
        url: 'https://offer-url.example.com',
        isDigital: true,
        withdrawalDetails: 'détails de retrait',
        bookingEmail: 'booking@example.com',
        venue: getOfferVenueFactory({
          name: 'ma venue',
          publicName: 'ma venue (nom public)',
          isVirtual: true,
          managingOfferer: getOfferManagingOffererFactory({
            name: 'mon offerer',
          }),
        }),
      }),
      subCategories,
      categories,
    }

    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))

    vi.spyOn(api, 'patchPublishOffer').mockResolvedValue(
      getIndividualOfferFactory()
    )
    vi.spyOn(api, 'getMusicTypes').mockResolvedValue(musicTypes)
  })

  const expectOfferFields = async () => {
    expect(await screen.findByText('Détails de l’offre')).toBeInTheDocument()
    expect(screen.getByText('Type d’offre')).toBeInTheDocument()
    expect(screen.getByText('Informations pratiques')).toBeInTheDocument()
    expect(screen.getByText('Modalités d’accessibilité')).toBeInTheDocument()
    expect(
      screen.getByText('Notifications des réservations')
    ).toBeInTheDocument()
    expect(screen.getByText('Aperçu dans l’app')).toBeInTheDocument()

    expect(screen.getByText(categories[0].proLabel)).toBeInTheDocument()
    expect(screen.getByText(subCategories[0].proLabel)).toBeInTheDocument()
    expect(screen.getByText('détails de retrait')).toBeInTheDocument()
    expect(screen.getByText('Non accessible')).toBeInTheDocument()
    expect(screen.getByText('booking@example.com')).toBeInTheDocument()
    expect(screen.getAllByText('mon offre')).toHaveLength(2)
    expect(screen.getAllByText('ma description')).toHaveLength(2)
  }

  it('should render component with informations on edition', async () => {
    renderIndividualOfferSummaryScreen({ contextValue: customContext })

    await expectOfferFields()
    expect(screen.getByText('Retour à la liste des offres')).toBeInTheDocument()
    expect(screen.getByText('Visualiser dans l’app')).toBeInTheDocument()
  })

  it('should render public name if available', async () => {
    renderIndividualOfferSummaryScreen({ contextValue: customContext })

    await expectOfferFields()
    expect(screen.getByText('ma venue (nom public)')).toBeInTheDocument()
  })

  it('should render name if no public name available', async () => {
    renderIndividualOfferSummaryScreen({
      contextValue: {
        ...customContext,
        offer: getIndividualOfferFactory({
          ...customContext.offer,
          venue: getOfferVenueFactory({
            name: 'ma venue (name)',
            publicName: null,
          }),
        }),
      },
    })

    await expectOfferFields()
    expect(screen.getByText('ma venue (name)')).toBeInTheDocument()
  })

  describe('On Creation', () => {
    beforeEach(() => {
      if (customContext.offer) {
        customContext.offer = {
          ...customContext.offer,
          status: OfferStatus.DRAFT,
        }
      }
    })

    it('should render component with informations', async () => {
      renderIndividualOfferSummaryScreen({
        contextValue: customContext,
        mode: OFFER_WIZARD_MODE.CREATION,
        path: generatePath(
          getIndividualOfferPath({
            step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: 'AA' }
        ),
      })

      await expectOfferFields()
      expect(
        screen.queryByText('Visualiser dans l’app')
      ).not.toBeInTheDocument()
    })

    it('should render a media section when media page is enabled (WIP_ADD_VIDEO)', () => {
      renderIndividualOfferSummaryScreen({
        contextValue: customContext,
        mode: OFFER_WIZARD_MODE.CREATION,
        path: generatePath(
          getIndividualOfferPath({
            step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: 'AA' }
        ),
        options: {
          features: ['WIP_ADD_VIDEO'],
        },
      })

      expect(
        screen.getByRole('heading', { name: 'Image et vidéo' })
      ).toBeInTheDocument()
    })

    it('should render component with new sections', async () => {
      vi.spyOn(api, 'getOfferer').mockResolvedValue(
        defaultGetOffererResponseModel
      )
      customContext.offer = getIndividualOfferFactory({ isEvent: true })

      renderIndividualOfferSummaryScreen({
        contextValue: customContext,
        mode: OFFER_WIZARD_MODE.CREATION,
        path: generatePath(
          getIndividualOfferPath({
            step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: 'AA' }
        ),
      })

      expect(
        await screen.findByText('À propos de votre offre')
      ).toBeInTheDocument()
    })

    it('should render component with right buttons', () => {
      renderIndividualOfferSummaryScreen({
        contextValue: customContext,
        mode: OFFER_WIZARD_MODE.CREATION,
        path: generatePath(
          getIndividualOfferPath({
            step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: 'AA' }
        ),
      })

      expect(screen.getByText('Retour')).toBeInTheDocument()
      expect(
        screen.getByText('Sauvegarder le brouillon et quitter')
      ).toBeInTheDocument()
      expect(screen.getByText('Publier l’offre')).toBeInTheDocument()
    })

    it('should link to creation confirmation page', async () => {
      vi.spyOn(api, 'getOfferer').mockResolvedValue(
        defaultGetOffererResponseModel
      )

      renderIndividualOfferSummaryScreen({
        contextValue: customContext,
        mode: OFFER_WIZARD_MODE.CREATION,
        path: generatePath(
          getIndividualOfferPath({
            step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: 'AA' }
        ),
      })

      await userEvent.click(
        screen.getByRole('button', { name: /Publier l’offre/ })
      )

      expect(
        await screen.findByText(/Confirmation page: creation/)
      ).toBeInTheDocument()
    })

    it('should disabled publish button link during submit', async () => {
      renderIndividualOfferSummaryScreen({
        contextValue: customContext,
        mode: OFFER_WIZARD_MODE.CREATION,
        path: generatePath(
          getIndividualOfferPath({
            step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: 'AA' }
        ),
      })

      const pageTitle = await screen.findByRole('heading', {
        name: /Détails de l’offre/,
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
      vi.spyOn(api, 'getOfferer').mockResolvedValue(
        defaultGetOffererResponseModel
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

      vi.spyOn(api, 'getOfferer').mockResolvedValue(
        defaultGetOffererResponseModel
      )
      customContext.offer = getIndividualOfferFactory()

      renderIndividualOfferSummaryScreen({
        contextValue: customContext,
        mode: OFFER_WIZARD_MODE.CREATION,
        path: generatePath(
          getIndividualOfferPath({
            step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: 'AA' }
        ),
      })

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
      await userEvent.selectOptions(screen.getByLabelText('Heure *'), '11:00')

      await userEvent.click(
        screen.getByRole('button', { name: 'Programmer l’offre' })
      )

      expect(
        await screen.findByText(/Confirmation page: creation/)
      ).toBeInTheDocument()
      expect(api.patchPublishOffer).toHaveBeenCalledWith({
        id: customContext.offer.id,
        publicationDatetime: `${publicationDate}T10:00:00Z`,
      })

      // Clean up the mocked time
      vi.useRealTimers()
    })

    it('should allow to maker offer bookable later if the FF WIP_REFACTO_FUTURE_OFFER is enabled', async () => {
      // Mock current date to avoid DST issues
      vi.setSystemTime(new Date('2024-01-15T12:00:00.000Z'))

      vi.spyOn(api, 'getOfferer').mockResolvedValue(
        defaultGetOffererResponseModel
      )
      customContext.offer = getIndividualOfferFactory()

      renderIndividualOfferSummaryScreen({
        contextValue: customContext,
        mode: OFFER_WIZARD_MODE.CREATION,
        path: generatePath(
          getIndividualOfferPath({
            step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: 'AA' }
        ),
        options: { features: ['WIP_REFACTO_FUTURE_OFFER'] },
      })

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
      await userEvent.selectOptions(screen.getByLabelText('Heure *'), '11:00')

      await userEvent.click(
        screen.getByRole('button', { name: 'Publier l’offre' })
      )

      expect(
        await screen.findByText(/Confirmation page: creation/)
      ).toBeInTheDocument()
      expect(api.patchPublishOffer).toHaveBeenCalledWith({
        id: customContext.offer.id,
        bookingAllowedDatetime: `${bookingAllowedDate}T10:00:00Z`,
      })

      // Clean up the mocked time
      vi.useRealTimers()
    })

    it('should display notification on api error', async () => {
      renderIndividualOfferSummaryScreen({
        contextValue: customContext,
        mode: OFFER_WIZARD_MODE.CREATION,
        path: generatePath(
          getIndividualOfferPath({
            step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: 'AA' }
        ),
      })

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

    it('should display redirect modal if first offer', async () => {
      const venueId = 1
      const context = {
        offer: getIndividualOfferFactory({
          venue: getOfferVenueFactory({ id: venueId }),
        }),
        showVenuePopin: {
          [venueId]: true,
        },
      }

      renderIndividualOfferSummaryScreen({
        contextValue: context,
        mode: OFFER_WIZARD_MODE.CREATION,
        path: generatePath(
          getIndividualOfferPath({
            step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: 'AA' }
        ),
      })

      await userEvent.click(
        screen.getByRole('button', { name: /Publier l’offre/ })
      )

      expect(
        await screen.findByText('Félicitations, vous avez créé votre offre !')
      ).toBeInTheDocument()
      expect(
        screen.getByRole('link', {
          name: 'Ajouter un compte bancaire',
        })
      ).toHaveAttribute(
        'href',
        `/remboursements/informations-bancaires?structure=${context.offer.venue.managingOfferer.id}`
      )
    })

    it('should display redirect modal if first non free offer', async () => {
      const context = {
        offer: getIndividualOfferFactory(),
        venueList: [venueListItemFactory()],
      }

      vi.spyOn(api, 'getOfferer').mockResolvedValue({
        ...defaultGetOffererResponseModel,
        hasValidBankAccount: false,
        hasPendingBankAccount: false,
        hasNonFreeOffer: false,
      })

      vi.spyOn(api, 'patchPublishOffer').mockResolvedValue(
        getIndividualOfferFactory({ isNonFreeOffer: true })
      )

      renderIndividualOfferSummaryScreen({
        contextValue: context,
        mode: OFFER_WIZARD_MODE.CREATION,
        path: generatePath(
          getIndividualOfferPath({
            step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: 'AA' }
        ),
        options: {},
      })

      await userEvent.click(
        screen.getByRole('button', { name: /Publier l’offre/ })
      )

      expect(
        await screen.findByText('Félicitations, vous avez créé votre offre !')
      ).toBeInTheDocument()
      expect(
        screen.getByRole('link', { name: 'Ajouter un compte bancaire' })
      ).toHaveAttribute(
        'href',
        `/remboursements/informations-bancaires?structure=${context.offer.venue.managingOfferer.id}`
      )
    })

    it('should not display redirect modal if hasPendingBankAccount is true', async () => {
      const context = {
        offer: getIndividualOfferFactory(),
        venueList: [venueListItemFactory()],
      }

      vi.spyOn(api, 'getOfferer').mockResolvedValue({
        ...defaultGetOffererResponseModel,
        hasValidBankAccount: true,
        hasPendingBankAccount: false,
      })

      vi.spyOn(api, 'patchPublishOffer').mockResolvedValue(
        getIndividualOfferFactory({ isNonFreeOffer: false })
      )

      renderIndividualOfferSummaryScreen({
        contextValue: context,
        mode: OFFER_WIZARD_MODE.CREATION,
        path: generatePath(
          getIndividualOfferPath({
            step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: 'AA' }
        ),
        options: {},
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

      const context = {
        offer: getIndividualOfferFactory(),
        venueList: [venueListItemFactory()],
      }

      renderIndividualOfferSummaryScreen({
        contextValue: context,
        mode: OFFER_WIZARD_MODE.CREATION,
        path: generatePath(
          getIndividualOfferPath({
            step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: 'AA' }
        ),
        options: {},
      })

      await userEvent.click(
        screen.getByRole('button', { name: /Publier l’offre/ })
      )

      expect(
        screen.queryByText('Félicitations, vous avez créé votre offre !')
      ).not.toBeInTheDocument()
    })

    it('should not display redirect modal if venue hasNonFreeOffers', async () => {
      vi.spyOn(api, 'getOfferer').mockResolvedValue({
        ...defaultGetOffererResponseModel,
        hasNonFreeOffer: true,
      })

      const context = {
        offer: getIndividualOfferFactory(),
        venueList: [venueListItemFactory()],
      }

      renderIndividualOfferSummaryScreen({
        contextValue: context,
        mode: OFFER_WIZARD_MODE.CREATION,
        path: generatePath(
          getIndividualOfferPath({
            step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: 'AA' }
        ),
        options: {},
      })

      await userEvent.click(
        screen.getByRole('button', { name: /Publier l’offre/ })
      )

      expect(
        screen.queryByText('Félicitations, vous avez créé votre offre !')
      ).not.toBeInTheDocument()
    })

    it('should render component with new sections and right address data', async () => {
      vi.spyOn(api, 'getOfferer').mockResolvedValue(
        defaultGetOffererResponseModel
      )
      customContext.offer = getIndividualOfferFactory({
        isEvent: true,
        address: {
          ...getAddressResponseIsLinkedToVenueModelFactory({
            label: 'mon adresse',
            city: 'ma ville',
            street: 'ma street',
            postalCode: '1',
          }),
        },
      })

      renderIndividualOfferSummaryScreen({
        contextValue: customContext,
        mode: OFFER_WIZARD_MODE.CREATION,
        path: generatePath(
          getIndividualOfferPath({
            step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: 'AA' }
        ),
      })

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

    it('should render component with new sections and empty address data', async () => {
      vi.spyOn(api, 'getOfferer').mockResolvedValue(
        defaultGetOffererResponseModel
      )
      customContext.offer = getIndividualOfferFactory({
        isEvent: true,
        address: null,
      })

      renderIndividualOfferSummaryScreen({
        contextValue: customContext,
        mode: OFFER_WIZARD_MODE.CREATION,
        path: generatePath(
          getIndividualOfferPath({
            step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: 'AA' }
        ),
      })

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
  })

  describe('banners', () => {
    it('should display pre publishing banner in creation', () => {
      const url = generatePath(
        getIndividualOfferPath({
          step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY,
          mode: OFFER_WIZARD_MODE.CREATION,
        }),
        { offerId: 'AA' }
      )
      renderIndividualOfferSummaryScreen({
        contextValue: customContext,
        mode: OFFER_WIZARD_MODE.CREATION,
        path: url,
      })

      expect(screen.getByText('Vous y êtes presque !')).toBeInTheDocument()
    })

    it('should display a notification when saving as draft', async () => {
      renderIndividualOfferSummaryScreen({
        contextValue: customContext,
        mode: OFFER_WIZARD_MODE.CREATION,
        path: generatePath(
          getIndividualOfferPath({
            step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: 'AA' }
        ),
      })
      await userEvent.click(
        screen.getByText('Sauvegarder le brouillon et quitter')
      )
      expect(
        screen.getByText('Brouillon sauvegardé dans la liste des offres')
      ).toBeInTheDocument()
    })

    it('should not display pre publishing banner in edition mode', () => {
      renderIndividualOfferSummaryScreen({
        contextValue: customContext,
        mode: OFFER_WIZARD_MODE.EDITION,
        path: generatePath(
          getIndividualOfferPath({
            step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.EDITION,
          }),
          { offerId: 'AA' }
        ),
      })

      expect(
        screen.queryByText('Vous y êtes presque !')
      ).not.toBeInTheDocument()
    })
  })
})

describe('Form', () => {
  const inOneMonth = set(add(new Date(), { months: 1 }), {
    hours: 10,
    minutes: 0,
  })

  let contextValue: IndividualOfferContextValues
  const mode = OFFER_WIZARD_MODE.CREATION
  const options: RenderWithProvidersOptions = {
    user: sharedCurrentUserFactory(),
    storeOverrides: {
      user: { currentUser: sharedCurrentUserFactory() },
      offerer: currentOffererFactory(),
    },
  }

  beforeEach(() => {
    const categories = [
      categoryFactory({
        id: 'A',
        proLabel: 'Catégorie A',
        isSelectable: true,
      }),
    ]
    const subCategories = [
      subcategoryFactory({
        id: 'virtual',
        categoryId: 'A',
        proLabel: 'Sous catégorie online de A',
        isEvent: false,
        canBeDuo: false,
        onlineOfflinePlatform: CATEGORY_STATUS.ONLINE,
      }),
      subcategoryFactory({
        id: 'physical',
        categoryId: 'A',
        proLabel: 'Sous catégorie offline de A',
        isEvent: false,
        conditionalFields: ['ean'],
        canBeDuo: true,
        canBeWithdrawable: false,
        onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
      }),
    ]

    contextValue = individualOfferContextValuesFactory({
      categories,
      offer: getIndividualOfferFactory({ id: 1 }),
      subCategories,
    })

    vi.spyOn(api, 'getOfferer').mockImplementation(vi.fn())
    vi.spyOn(api, 'patchPublishOffer').mockResolvedValue(
      getIndividualOfferFactory()
    )
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  it("should validate publication date and time when it's a scheduled publication", async () => {
    renderIndividualOfferSummaryScreen({ contextValue, mode, options })

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
    const publicationTimeSelect = screen.getByLabelText(
      LABELS.publicationTimeSelect
    )

    await userEvent.type(publicationDateInput, format(inOneMonth, 'yyyy-MM-dd'))

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
      id: contextValue.offer!.id,
      publicationDatetime: expect.any(String),
      bookingAllowedDatetime: undefined,
    })
  })

  it("should require publication date to be in the future when it's a scheduled publication", async () => {
    const yesterday = set(sub(new Date(), { days: 1 }), {
      hours: 10,
      minutes: 0,
    })

    renderIndividualOfferSummaryScreen({ contextValue, mode, options })

    await userEvent.click(
      screen.getByLabelText(LABELS.publicationModeLaterRadio)
    )

    const publicationDateInput = screen.getByLabelText(
      LABELS.publicationDateInput
    )
    const publicationTimeSelect = screen.getByLabelText(
      LABELS.publicationTimeSelect
    )

    await userEvent.type(publicationDateInput, format(yesterday, 'yyyy-MM-dd'))
    await userEvent.selectOptions(
      publicationTimeSelect,
      format(yesterday, 'HH:mm')
    )

    expect(
      await screen.findByText(ERROR_MESSAGES.publicationDateMustBeInFuture)
    ).toBeVisible()

    await userEvent.clear(publicationDateInput)
    await userEvent.type(publicationDateInput, format(inOneMonth, 'yyyy-MM-dd'))

    expect(
      screen.queryByTestId('error-publicationDate')
    ).not.toBeInTheDocument()

    await userEvent.click(
      screen.getByRole('button', { name: LABELS.submitScheduledOfferButton })
    )

    expect(api.patchPublishOffer).toHaveBeenCalledWith({
      id: contextValue.offer!.id,
      publicationDatetime: expect.any(String),
      bookingAllowedDatetime: undefined,
    })
  })

  it("should require publication date to be within two years when it's a scheduled publication", async () => {
    const inMoreThanTwoYears = set(add(new Date(), { months: 25 }), {
      hours: 10,
      minutes: 0,
    })

    renderIndividualOfferSummaryScreen({ contextValue, mode, options })

    await userEvent.click(
      screen.getByLabelText(LABELS.publicationModeLaterRadio)
    )

    const publicationDateInput = screen.getByLabelText(
      LABELS.publicationDateInput
    )
    const publicationTimeSelect = screen.getByLabelText(
      LABELS.publicationTimeSelect
    )

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
      id: contextValue.offer!.id,
      publicationDatetime: expect.any(String),
      bookingAllowedDatetime: undefined,
    })
  })
})
