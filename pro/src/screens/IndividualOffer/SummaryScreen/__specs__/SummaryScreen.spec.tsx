import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'
import { generatePath, Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import {
  ApiError,
  CancelablePromise,
  GetIndividualOfferResponseModel,
  OfferStatus,
} from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import Notification from 'components/Notification/Notification'
import {
  IndividualOfferContext,
  IndividualOfferContextValues,
} from 'context/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { getIndividualOfferPath } from 'core/Offers/utils/getIndividualOfferUrl'
import * as useAnalytics from 'hooks/useAnalytics'
import {
  defaultGetOffererResponseModel,
  GetIndividualOfferFactory,
  offererFactory,
  offerVenueFactory,
} from 'utils/apiFactories'
import {
  individualOfferCategoryFactory,
  individualOfferContextFactory,
  individualOfferFactory,
  individualOfferSubCategoryFactory,
  individualOfferVenueItemFactory,
  individualStockFactory,
} from 'utils/individualApiFactories'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'utils/renderWithProviders'

import SummaryScreen from '../SummaryScreen'

const mockLogEvent = vi.fn()

const renderSummary = (
  customContext: Partial<IndividualOfferContextValues> = {},
  url: string = getIndividualOfferPath({
    step: OFFER_WIZARD_STEP_IDS.SUMMARY,
    mode: OFFER_WIZARD_MODE.READ_ONLY,
  }),
  options?: RenderWithProvidersOptions
) => {
  const contextValues = individualOfferContextFactory(customContext)

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

const categories = [individualOfferCategoryFactory({ id: 'A' })]

const subCategories = [
  individualOfferSubCategoryFactory({ categoryId: 'A' }),
  individualOfferSubCategoryFactory({ categoryId: 'A' }),
]

describe('Summary', () => {
  let customContext: Partial<IndividualOfferContextValues>
  beforeEach(() => {
    customContext = {
      offer: individualOfferFactory({
        isEvent: false,
        name: 'mon offre',
        lastProvider: {
          name: 'Ciné Office',
        },
        lastProviderName: 'Ciné Office',
        accessibility: {
          visual: false,
          audio: false,
          motor: false,
          mental: false,
          none: true,
        },
        description: 'ma description',
        subcategoryId: subCategories[0].id,
        url: 'https://offer-url.example.com',
        withdrawalDetails: 'détails de retrait',
        externalTicketOfficeUrl: 'https://grand-public-url.example.com',
        bookingEmail: 'booking@example.com',
        venue: offerVenueFactory(
          {
            name: 'ma venue',
            publicName: 'ma venue (nom public)',
            isVirtual: true,
          },
          offererFactory({ name: 'mon offerer' })
        ),
      }),
      subCategories,
      categories,
    }

    vi.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
    vi.spyOn(api, 'patchPublishOffer').mockResolvedValue(
      GetIndividualOfferFactory()
    )
  })

  const expectOfferFields = () => {
    expect(screen.getByText('Détails de l’offre')).toBeInTheDocument()
    expect(screen.getByText('Type d’offre')).toBeInTheDocument()
    expect(screen.getByText('Informations artistiques')).toBeInTheDocument()
    expect(screen.getByText('Informations pratiques')).toBeInTheDocument()
    expect(screen.getByText('Accessibilité')).toBeInTheDocument()
    expect(
      screen.getByText('Notifications des réservations')
    ).toBeInTheDocument()
    expect(
      screen.getByText('URL d’accès à l’offre', { exact: false })
    ).toBeInTheDocument()
    expect(screen.getByText('Lien pour le grand public')).toBeInTheDocument()
    expect(screen.getByText('Aperçu dans l’app')).toBeInTheDocument()

    expect(screen.getByText(categories[0].proLabel)).toBeInTheDocument()
    expect(screen.getByText(subCategories[0].proLabel)).toBeInTheDocument()
    expect(screen.getByText('mon offerer')).toBeInTheDocument()
    expect(screen.getByText('ma venue (nom public)')).toBeInTheDocument()
    expect(screen.getByText('détails de retrait')).toBeInTheDocument()
    expect(
      screen.getByText('https://offer-url.example.com')
    ).toBeInTheDocument()
    expect(
      screen.getByText('https://grand-public-url.example.com')
    ).toBeInTheDocument()
    expect(screen.getByText('Non accessible')).toBeInTheDocument()
    expect(screen.getByText('booking@example.com')).toBeInTheDocument()
    expect(screen.getAllByText('mon offre')).toHaveLength(2)
    expect(screen.getAllByText('ma description')).toHaveLength(2)
  }

  describe('On edition', () => {
    it('should render component with informations', () => {
      // given / when
      renderSummary(customContext)

      // then
      expectOfferFields()
      expect(
        screen.getByText('Retour à la liste des offres')
      ).toBeInTheDocument()
      expect(screen.getByText('Visualiser dans l’app')).toBeInTheDocument()
    })
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

    it('should render component with informations', () => {
      // given / when
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

      // then
      expectOfferFields()
      expect(
        screen.queryByText('Visualiser dans l’app')
      ).not.toBeInTheDocument()
    })

    describe('When it is form v3', () => {
      it('should render component with right buttons', () => {
        // when
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

        // then
        expect(screen.getByText('Retour')).toBeInTheDocument()
        expect(
          screen.getByText('Sauvegarder le brouillon et quitter')
        ).toBeInTheDocument()
        expect(screen.getByText('Publier l’offre')).toBeInTheDocument()
      })

      it('should link to creation confirmation page', async () => {
        // when
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
    })

    it('should disabled publish button link during submit', async () => {
      // when
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

      const pageTitle = screen.getByRole('heading', {
        name: /Détails de l’offre/,
      })
      const buttonPublish = screen.getByRole('button', {
        name: /Publier l’offre/,
      })
      expect(buttonPublish).not.toBeDisabled()

      const mockResponse =
        new CancelablePromise<GetIndividualOfferResponseModel>((resolve) =>
          setTimeout(() => {
            resolve(GetIndividualOfferFactory())
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

    it('should display notification on api error', async () => {
      // when
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
        offer: individualOfferFactory({
          venue: offerVenueFactory({ id: venueId }),
        }),
        offerOfferer: { name: 'offerOffererName', id: 1 },
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
          name: 'Renseigner des coordonnées bancaires',
        })
      ).toHaveAttribute(
        'href',
        '/structures/1/lieux/1?modification#remboursement'
      )
    })

    it('should display redirect modal if first non free offer', async () => {
      const context = {
        offer: individualOfferFactory(
          individualStockFactory({ price: 2, quantity: null })
        ),
        offerOfferer: { name: 'offerOffererName', id: 1 },
        venueList: [individualOfferVenueItemFactory()],
      }

      vi.spyOn(api, 'getOfferer').mockResolvedValue({
        ...defaultGetOffererResponseModel,
        hasValidBankAccount: false,
        hasPendingBankAccount: false,
        hasNonFreeOffer: false,
      })

      vi.spyOn(api, 'patchPublishOffer').mockResolvedValue(
        GetIndividualOfferFactory({ isNonFreeOffer: true })
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
          features: [
            'WIP_ENABLE_NEW_OFFER_CREATION_JOURNEY',
            'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY',
          ],
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
        '/remboursements/informations-bancaires?structure=1'
      )
    })

    it('should not display redirect modal if hasPendingBankAccount is true', async () => {
      const context = {
        offer: individualOfferFactory(
          individualStockFactory({ price: 2, quantity: null })
        ),
        offerOfferer: { name: 'offerOffererName', id: 1 },
        venueList: [individualOfferVenueItemFactory()],
      }

      vi.spyOn(api, 'getOfferer').mockResolvedValue({
        ...defaultGetOffererResponseModel,
        hasValidBankAccount: true,
        hasPendingBankAccount: false,
      })

      vi.spyOn(api, 'patchPublishOffer').mockResolvedValue(
        GetIndividualOfferFactory({ isNonFreeOffer: false })
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
          features: [
            'WIP_ENABLE_NEW_OFFER_CREATION_JOURNEY',
            'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY',
          ],
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
      const context = {
        offer: individualOfferFactory(),
        venueList: [individualOfferVenueItemFactory()],
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
          features: [
            'WIP_ENABLE_NEW_OFFER_CREATION_JOURNEY',
            'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY',
          ],
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
      const context = {
        offer: individualOfferFactory(),
        venueList: [individualOfferVenueItemFactory()],
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
          features: [
            'WIP_ENABLE_NEW_OFFER_CREATION_JOURNEY',
            'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY',
          ],
        }
      )

      await userEvent.click(
        screen.getByRole('button', { name: /Publier l’offre/ })
      )

      expect(
        screen.queryByText('Félicitations, vous avez créé votre offre !')
      ).not.toBeInTheDocument()
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
