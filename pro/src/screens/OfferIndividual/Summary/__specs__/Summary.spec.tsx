import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
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
import Notification from 'components/Notification/Notification'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import {
  IOfferIndividualContext,
  OfferIndividualContext,
} from 'context/OfferIndividualContext'
import { OFFER_WIZARD_MODE } from 'core/Offers'
import { getOfferIndividualPath } from 'core/Offers/utils/getOfferIndividualUrl'
import * as useAnalytics from 'hooks/useAnalytics'
import * as useNewOfferCreationJourney from 'hooks/useNewOfferCreationJourney'
import {
  individualOfferCategoryFactory,
  individualOfferFactory,
  individualOfferOffererFactory,
  individualOfferSubCategoryFactory,
  individualOfferVenueFactory,
  individualStockFactory,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import Summary from '../Summary'

const mockLogEvent = jest.fn()

jest.mock('core/Notification/constants', () => ({
  NOTIFICATION_TRANSITION_DURATION: 10,
  NOTIFICATION_SHOW_DURATION: 10,
}))

const renderSummary = (
  customContext: Partial<IOfferIndividualContext> = {},
  url: string = getOfferIndividualPath({
    step: OFFER_WIZARD_STEP_IDS.SUMMARY,
    mode: OFFER_WIZARD_MODE.EDITION,
  }),
  storeOverride: any = {}
) => {
  const contextValues: IOfferIndividualContext = {
    offerId: null,
    offer: null,
    venueList: [],
    offererNames: [],
    categories: [],
    subCategories: [],
    setOffer: () => {},
    setShouldTrack: () => {},
    shouldTrack: true,
    showVenuePopin: {},
    ...customContext,
  }

  const storeOverrides = {
    user: {
      initialized: true,
      currentUser: {
        isAdmin: false,
        email: 'email@example.com',
      },
    },
    ...storeOverride,
  }

  return renderWithProviders(
    <>
      <OfferIndividualContext.Provider value={contextValues}>
        <Routes>
          <Route
            path={getOfferIndividualPath({
              step: OFFER_WIZARD_STEP_IDS.SUMMARY,
              mode: OFFER_WIZARD_MODE.EDITION,
            })}
            element={<Summary />}
          />
          <Route
            path={getOfferIndividualPath({
              step: OFFER_WIZARD_STEP_IDS.SUMMARY,
              mode: OFFER_WIZARD_MODE.CREATION,
            })}
            element={<Summary />}
          />
          <Route
            path={getOfferIndividualPath({
              step: OFFER_WIZARD_STEP_IDS.SUMMARY,
              mode: OFFER_WIZARD_MODE.DRAFT,
            })}
            element={<Summary />}
          />
          <Route
            path={getOfferIndividualPath({
              step: OFFER_WIZARD_STEP_IDS.CONFIRMATION,
              mode: OFFER_WIZARD_MODE.DRAFT,
            })}
            element={<div>Confirmation page: draft</div>}
          />
          <Route
            path={getOfferIndividualPath({
              step: OFFER_WIZARD_STEP_IDS.CONFIRMATION,
              mode: OFFER_WIZARD_MODE.CREATION,
            })}
            element={<div>Confirmation page: creation</div>}
          />
          <Route
            path={getOfferIndividualPath({
              step: OFFER_WIZARD_STEP_IDS.CONFIRMATION,
              mode: OFFER_WIZARD_MODE.DRAFT,
              isV2: true,
            })}
            element={<div>Confirmation page: draft V2</div>}
          />
          <Route
            path={getOfferIndividualPath({
              step: OFFER_WIZARD_STEP_IDS.CONFIRMATION,
              mode: OFFER_WIZARD_MODE.CREATION,
              isV2: true,
            })}
            element={<div>Confirmation page: creation V2</div>}
          />
        </Routes>
      </OfferIndividualContext.Provider>
      <Notification />
    </>,
    { storeOverrides, initialRouterEntries: [url] }
  )
}

jest.mock('hooks/useNewOfferCreationJourney', () => ({
  __esModule: true,
  default: jest.fn().mockReturnValue(false),
}))

const categories = [individualOfferCategoryFactory({ id: 'A' })]

const subCategories = [
  individualOfferSubCategoryFactory({ categoryId: 'A' }),
  individualOfferSubCategoryFactory({ categoryId: 'A' }),
]

describe('Summary', () => {
  let customContext: Partial<IOfferIndividualContext>
  beforeEach(() => {
    customContext = {
      offer: individualOfferFactory(
        {
          id: 'AA',
          isEvent: false,
          name: 'mon offre',
          lastProvider: {
            id: 'ciné office',
            isActive: true,
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
        },
        individualStockFactory({ price: 0, quantity: null }),
        individualOfferVenueFactory(
          {
            name: 'ma venue',
            publicName: 'ma venue (nom public)',
            isVirtual: true,
          },
          individualOfferOffererFactory({ name: 'mon offerer' })
        )
      ),
      subCategories,
      categories,
    }

    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
    jest.spyOn(api, 'patchPublishOffer').mockResolvedValue()
    jest.spyOn(api, 'getOffer').mockResolvedValue({
      status: OfferStatus.ACTIVE,
    } as GetIndividualOfferResponseModel)
  })

  const expectOfferFields = () => {
    expect(
      screen.getByText('Offre synchronisée avec Ciné Office')
    ).toBeInTheDocument()
    expect(screen.getAllByText('Modifier')).toHaveLength(2)
    expect(screen.getByText('Détails de l’offre')).toBeInTheDocument()
    expect(screen.getByText('Type d’offre')).toBeInTheDocument()
    expect(screen.getByText('Informations artistiques')).toBeInTheDocument()
    expect(screen.getByText('Informations pratiques')).toBeInTheDocument()
    expect(screen.getByText('Accessibilité')).toBeInTheDocument()
    expect(
      screen.getByText('Notifications des réservations')
    ).toBeInTheDocument()
    expect(screen.getByText('Stocks et prix')).toBeInTheDocument()
    expect(
      screen.getByText('URL d’accès à l’offre', { exact: false })
    ).toBeInTheDocument()
    expect(screen.getByText('Lien pour le grand public')).toBeInTheDocument()
    expect(screen.getByText("Aperçu dans l'app")).toBeInTheDocument()

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
    expect(screen.getByText('0 €')).toBeInTheDocument()
    expect(screen.getByText('Illimité')).toBeInTheDocument()
    expect(screen.getAllByText('mon offre')).toHaveLength(2)
    expect(screen.getAllByText('ma description')).toHaveLength(2)
  }

  describe('On edition', () => {
    it('should render component with informations', async () => {
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

    it('should render component with informations', async () => {
      // given / when
      renderSummary(
        customContext,
        generatePath(
          getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: 'AA' }
        )
      )

      // then
      expect(screen.getAllByText('Modifier')).toHaveLength(2)
      expectOfferFields()
      expect(
        screen.queryByText('Visualiser dans l’app')
      ).not.toBeInTheDocument()
    })

    describe('When it is form v3', () => {
      it('should render component with right buttons', async () => {
        // when
        renderSummary(
          customContext,
          generatePath(
            getOfferIndividualPath({
              step: OFFER_WIZARD_STEP_IDS.SUMMARY,
              mode: OFFER_WIZARD_MODE.CREATION,
            }),
            { offerId: 'AA' }
          )
        )

        // then
        expect(screen.getByText('Étape précédente')).toBeInTheDocument()
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
            getOfferIndividualPath({
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
          getOfferIndividualPath({
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

      const mockResponse = new CancelablePromise<void>(async resolve =>
        setTimeout(() => {
          resolve(undefined)
        }, 200)
      )
      jest.spyOn(api, 'patchPublishOffer').mockResolvedValue(mockResponse)
      await userEvent.click(buttonPublish)
      expect(api.patchPublishOffer).toHaveBeenCalled()
      expect(buttonPublish).toBeDisabled()
      await waitFor(() => expect(pageTitle).not.toBeInTheDocument())
      expect(
        screen.getByText('Confirmation page: creation')
      ).toBeInTheDocument()
    })

    // TODO investigate why this test is flaky
    it.skip('should display notification on api error', async () => {
      // when
      renderSummary(
        customContext,
        generatePath(
          getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: 'AA' }
        )
      )

      jest.spyOn(api, 'patchPublishOffer').mockRejectedValue(
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
        await screen.findByText("Une erreur s'est produite, veuillez réessayer")
      ).toBeInTheDocument()
    })

    it('should display redirect modal if first offer', async () => {
      jest.spyOn(useNewOfferCreationJourney, 'default').mockReturnValue(true)

      const context = {
        offer: individualOfferFactory({ id: 'AA' }),
        venueId: 1,
        showVenuePopin: {
          1: true,
        },
      }
      const storeOverride = {
        features: {
          initialized: true,
          list: [
            {
              isActive: true,
              nameKey: 'WIP_ENABLE_NEW_OFFER_CREATION_JOURNEY',
            },
          ],
        },
      }

      renderSummary(
        context,
        generatePath(
          getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: 'AA' }
        ),
        storeOverride
      )

      await userEvent.click(
        screen.getByRole('button', { name: /Publier l’offre/ })
      )

      expect(
        await screen.findByText('Félicitations, vous avez créé votre offre !')
      ).toBeInTheDocument()
    })
  })

  describe('banners', () => {
    const urlList = [
      generatePath(
        getOfferIndividualPath({
          step: OFFER_WIZARD_STEP_IDS.SUMMARY,
          mode: OFFER_WIZARD_MODE.CREATION,
        }),
        { offerId: 'AA' }
      ),
      generatePath(
        getOfferIndividualPath({
          step: OFFER_WIZARD_STEP_IDS.SUMMARY,
          mode: OFFER_WIZARD_MODE.DRAFT,
        }),
        { offerId: 'AA' }
      ),
    ]
    it.each(urlList)(
      'should display pre publishing banner in creation',
      url => {
        renderSummary(customContext, url)

        // then
        expect(screen.getByText('Vous y êtes presque !')).toBeInTheDocument()
      }
    )

    it('should display a notification when saving as draft', async () => {
      // when
      renderSummary(
        customContext,
        generatePath(
          getOfferIndividualPath({
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
      // when
      renderSummary(
        customContext,
        generatePath(
          getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.EDITION,
          }),
          { offerId: 'AA' }
        )
      )

      // then
      expect(
        screen.queryByText('Vous y êtes presque !')
      ).not.toBeInTheDocument()
    })
  })
})
