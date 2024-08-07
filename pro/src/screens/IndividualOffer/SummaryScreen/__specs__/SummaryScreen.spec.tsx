import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { addDays, format } from 'date-fns'
import { generatePath, Route, Routes } from 'react-router-dom'
import { expect } from 'vitest'

import { api } from 'apiClient/api'
import {
  ApiError,
  CancelablePromise,
  GetIndividualOfferResponseModel,
  GetMusicTypesResponse,
  OfferStatus,
  SubcategoryIdEnum,
} from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import * as useAnalytics from 'app/App/analytics/firebase'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { Notification } from 'components/Notification/Notification'
import {
  IndividualOfferContext,
  IndividualOfferContextValues,
} from 'context/IndividualOfferContext/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { getIndividualOfferPath } from 'core/Offers/utils/getIndividualOfferUrl'
import { addressResponseIsEditableModelFactory } from 'utils/commonOffersApiFactories'
import { FORMAT_ISO_DATE_ONLY } from 'utils/date'
import {
  categoryFactory,
  defaultGetOffererResponseModel,
  getIndividualOfferFactory,
  getOfferManagingOffererFactory,
  getOfferVenueFactory,
  individualOfferContextValuesFactory,
  subcategoryFactory,
  venueListItemFactory,
} from 'utils/individualApiFactories'
import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'utils/renderWithProviders'

import { SummaryScreen } from '../SummaryScreen'

const mockLogEvent = vi.fn()

const renderSummary = (
  customContext: Partial<IndividualOfferContextValues> = {},
  url: string = getIndividualOfferPath({
    step: OFFER_WIZARD_STEP_IDS.SUMMARY,
    mode: OFFER_WIZARD_MODE.READ_ONLY,
  }),
  options?: RenderWithProvidersOptions
) => {
  const contextValues = individualOfferContextValuesFactory(customContext)

  return renderWithProviders(
    <>
      <IndividualOfferContext.Provider value={contextValues}>
        <Routes>
          <Route
            path={getIndividualOfferPath({
              step: OFFER_WIZARD_STEP_IDS.SUMMARY,
              mode: OFFER_WIZARD_MODE.READ_ONLY,
            })}
            element={<SummaryScreen />}
          />
          <Route
            path={getIndividualOfferPath({
              step: OFFER_WIZARD_STEP_IDS.SUMMARY,
              mode: OFFER_WIZARD_MODE.CREATION,
            })}
            element={<SummaryScreen />}
          />
          <Route
            path={getIndividualOfferPath({
              step: OFFER_WIZARD_STEP_IDS.CONFIRMATION,
              mode: OFFER_WIZARD_MODE.CREATION,
            })}
            element={<div>Confirmation page: creation</div>}
          />
        </Routes>
      </IndividualOfferContext.Provider>
      <Notification />
    </>,
    { initialRouterEntries: [url], ...options }
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

describe('Summary', () => {
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
    expect(screen.getByText('Informations artistiques')).toBeInTheDocument()
    expect(screen.getByText('Informations pratiques')).toBeInTheDocument()
    expect(screen.getByText('Modalités d’accessibilité')).toBeInTheDocument()
    expect(
      screen.getByText('Notifications des réservations')
    ).toBeInTheDocument()
    expect(
      screen.getByText('URL d’accès à l’offre', { exact: false })
    ).toBeInTheDocument()
    expect(screen.getByText('Aperçu dans l’app')).toBeInTheDocument()

    expect(screen.getByText(categories[0].proLabel)).toBeInTheDocument()
    expect(screen.getByText(subCategories[0].proLabel)).toBeInTheDocument()
    expect(screen.getByText('mon offerer')).toBeInTheDocument()
    expect(screen.getByText('ma venue (nom public)')).toBeInTheDocument()
    expect(screen.getByText('détails de retrait')).toBeInTheDocument()
    expect(
      screen.getByText('https://offer-url.example.com')
    ).toBeInTheDocument()
    expect(screen.getByText('Non accessible')).toBeInTheDocument()
    expect(screen.getByText('booking@example.com')).toBeInTheDocument()
    expect(screen.getAllByText('mon offre')).toHaveLength(2)
    expect(screen.getAllByText('ma description')).toHaveLength(2)
  }

  it('should render component with informations on edition', async () => {
    renderSummary(customContext)

    await expectOfferFields()
    expect(screen.getByText('Retour à la liste des offres')).toBeInTheDocument()
    expect(screen.getByText('Visualiser dans l’app')).toBeInTheDocument()
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
      renderSummary(
        customContext,
        generatePath(
          getIndividualOfferPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: 'AA' }
        )
      )

      await expectOfferFields()
      expect(
        screen.queryByText('Visualiser dans l’app')
      ).not.toBeInTheDocument()
    })
    it('should render component with new sections', async () => {
      vi.spyOn(api, 'getOfferer').mockResolvedValue(
        defaultGetOffererResponseModel
      )
      customContext.offer = getIndividualOfferFactory({ isEvent: true })

      renderSummary(
        customContext,
        generatePath(
          getIndividualOfferPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: 'AA' }
        ),
        { features: ['WIP_SPLIT_OFFER'] }
      )

      expect(
        await screen.findByText('À propos de votre offre')
      ).toBeInTheDocument()
    })

    it('should render component with right buttons', () => {
      renderSummary(
        customContext,
        generatePath(
          getIndividualOfferPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: 'AA' }
        )
      )

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

      renderSummary(
        customContext,
        generatePath(
          getIndividualOfferPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: 'AA' }
        )
      )

      await userEvent.click(
        screen.getByRole('button', { name: /Publier l’offre/ })
      )

      expect(
        await screen.findByText(/Confirmation page: creation/)
      ).toBeInTheDocument()
    })

    it('should disabled publish button link during submit', async () => {
      renderSummary(
        customContext,
        generatePath(
          getIndividualOfferPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: 'AA' }
        )
      )

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

    it('should allow to publish offer later if the offer is an event', async () => {
      vi.spyOn(api, 'getOfferer').mockResolvedValue(
        defaultGetOffererResponseModel
      )
      customContext.offer = getIndividualOfferFactory({ isEvent: true })

      renderSummary(
        customContext,
        generatePath(
          getIndividualOfferPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: 'AA' }
        )
      )

      await userEvent.click(
        screen.getByLabelText('À une date et heure précise')
      )

      await userEvent.click(
        screen.getByRole('button', { name: 'Publier l’offre' })
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

      await userEvent.type(
        screen.getByLabelText('Date de publication *'),
        publicationDate
      )
      await userEvent.selectOptions(
        screen.getByLabelText('Heure de publication *'),
        '11:00'
      )

      await userEvent.click(
        screen.getByRole('button', { name: 'Publier l’offre' })
      )

      expect(
        await screen.findByText(/Confirmation page: creation/)
      ).toBeInTheDocument()
      expect(api.patchPublishOffer).toHaveBeenCalledWith({
        id: customContext.offer.id,
        publicationDate: `${publicationDate}T09:00:00Z`,
      })
    })

    it('should display notification on api error', async () => {
      renderSummary(
        customContext,
        generatePath(
          getIndividualOfferPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: 'AA' }
        )
      )

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

      renderSummary(
        context,
        generatePath(
          getIndividualOfferPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: 'AA' }
        ),
        { features: ['WIP_ENABLE_NEW_OFFER_CREATION_JOURNEY'] }
      )

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

      renderSummary(
        context,
        generatePath(
          getIndividualOfferPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: 'AA' }
        ),
        {
          features: ['WIP_ENABLE_NEW_OFFER_CREATION_JOURNEY'],
        }
      )

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

      renderSummary(
        context,
        generatePath(
          getIndividualOfferPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: 'AA' }
        ),
        {
          features: ['WIP_ENABLE_NEW_OFFER_CREATION_JOURNEY'],
        }
      )

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

      renderSummary(
        context,
        generatePath(
          getIndividualOfferPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: 'AA' }
        ),
        {
          features: ['WIP_ENABLE_NEW_OFFER_CREATION_JOURNEY'],
        }
      )

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

      renderSummary(
        context,
        generatePath(
          getIndividualOfferPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: 'AA' }
        ),
        {
          features: ['WIP_ENABLE_NEW_OFFER_CREATION_JOURNEY'],
        }
      )

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
          ...addressResponseIsEditableModelFactory({
            label: 'mon adresse',
            city: 'ma ville',
            street: 'ma street',
            postalCode: '1',
          }),
        },
      })

      renderSummary(
        customContext,
        generatePath(
          getIndividualOfferPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: 'AA' }
        ),
        { features: ['WIP_SPLIT_OFFER', 'WIP_ENABLE_OFFER_ADDRESS'] }
      )

      expect(await screen.findByText(/Qui propose l’offre/)).toBeInTheDocument()
      expect(
        await screen.findByText('Localisation de l’offre')
      ).toBeInTheDocument()

      expect(
        await screen.findByText('mon adresse - ma street 1 ma ville')
      ).toBeInTheDocument()
    })
  })

  describe('banners', () => {
    it('should display pre publishing banner in creation', () => {
      const url = generatePath(
        getIndividualOfferPath({
          step: OFFER_WIZARD_STEP_IDS.SUMMARY,
          mode: OFFER_WIZARD_MODE.CREATION,
        }),
        { offerId: 'AA' }
      )
      renderSummary(customContext, url)

      expect(screen.getByText('Vous y êtes presque !')).toBeInTheDocument()
    })

    it('should display a notification when saving as draft', async () => {
      renderSummary(
        customContext,
        generatePath(
          getIndividualOfferPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: 'AA' }
        )
      )
      await userEvent.click(
        screen.getByText('Sauvegarder le brouillon et quitter')
      )
      expect(
        screen.getByText('Brouillon sauvegardé dans la liste des offres')
      ).toBeInTheDocument()
    })

    it('should not display pre publishing banner in edition mode', () => {
      renderSummary(
        customContext,
        generatePath(
          getIndividualOfferPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.EDITION,
          }),
          { offerId: 'AA' }
        )
      )

      expect(
        screen.queryByText('Vous y êtes presque !')
      ).not.toBeInTheDocument()
    })
  })
})
