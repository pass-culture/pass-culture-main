import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { generatePath, MemoryRouter, Route } from 'react-router'

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
import { REIMBURSEMENT_RULES } from 'core/Finances'
import { CATEGORY_STATUS, OFFER_WIZARD_MODE } from 'core/Offers'
import { getOfferIndividualPath } from 'core/Offers/utils/getOfferIndividualUrl'
import * as useAnalytics from 'hooks/useAnalytics'
import * as useNewOfferCreationJourney from 'hooks/useNewOfferCreationJourney'
import { RootState } from 'store/reducers'
import { configureTestStore } from 'store/testUtils'

import Summary, { ISummaryProps } from '../Summary'

const mockLogEvent = jest.fn()

jest.mock('core/Notification/constants', () => ({
  NOTIFICATION_TRANSITION_DURATION: 10,
  NOTIFICATION_SHOW_DURATION: 10,
}))

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
}

const renderSummary = ({
  props,
  storeOverride = {},
  url = getOfferIndividualPath({
    step: OFFER_WIZARD_STEP_IDS.SUMMARY,
    mode: OFFER_WIZARD_MODE.EDITION,
  }),
  context = contextValues,
}: {
  props: ISummaryProps
  storeOverride?: Partial<RootState>
  url?: string
  context?: IOfferIndividualContext
}) => {
  const store = configureTestStore({
    user: {
      initialized: true,
      currentUser: {
        publicName: 'John Do',
        isAdmin: false,
        email: 'email@example.com',
      },
    },
    ...storeOverride,
  })
  return render(
    <Provider store={store}>
      <MemoryRouter initialEntries={[url]}>
        <OfferIndividualContext.Provider value={context}>
          <Route
            path={getOfferIndividualPath({
              step: OFFER_WIZARD_STEP_IDS.SUMMARY,
              mode: OFFER_WIZARD_MODE.EDITION,
            })}
          >
            <Summary {...props} />
          </Route>
          <Route
            path={getOfferIndividualPath({
              step: OFFER_WIZARD_STEP_IDS.SUMMARY,
              mode: OFFER_WIZARD_MODE.CREATION,
            })}
          >
            <Summary {...props} />
          </Route>
          <Route
            path={getOfferIndividualPath({
              step: OFFER_WIZARD_STEP_IDS.SUMMARY,
              mode: OFFER_WIZARD_MODE.DRAFT,
            })}
          >
            <Summary {...props} />
          </Route>
          <Route
            path={getOfferIndividualPath({
              step: OFFER_WIZARD_STEP_IDS.CONFIRMATION,
              mode: OFFER_WIZARD_MODE.DRAFT,
            })}
          >
            <div>Confirmation page: draft</div>
          </Route>
          <Route
            path={getOfferIndividualPath({
              step: OFFER_WIZARD_STEP_IDS.CONFIRMATION,
              mode: OFFER_WIZARD_MODE.CREATION,
            })}
          >
            <div>Confirmation page: creation</div>
          </Route>
          <Route
            path={getOfferIndividualPath({
              step: OFFER_WIZARD_STEP_IDS.CONFIRMATION,
              mode: OFFER_WIZARD_MODE.DRAFT,
              isV2: true,
            })}
          >
            <div>Confirmation page: draft V2</div>
          </Route>
          <Route
            path={getOfferIndividualPath({
              step: OFFER_WIZARD_STEP_IDS.CONFIRMATION,
              mode: OFFER_WIZARD_MODE.CREATION,
              isV2: true,
            })}
          >
            <div>Confirmation page: creation V2</div>
          </Route>
        </OfferIndividualContext.Provider>
      </MemoryRouter>
      <Notification />
    </Provider>
  )
}

jest.mock('hooks/useNewOfferCreationJourney', () => ({
  __esModule: true,
  default: jest.fn().mockReturnValue(false),
}))

describe('Summary', () => {
  let props: ISummaryProps
  beforeEach(() => {
    const categories = [
      {
        id: 'A',
        proLabel: 'Catégorie A',
        isSelectable: true,
      },
    ]
    const subCategories = [
      {
        id: 'A-A',
        categoryId: 'A',
        proLabel: 'Sous catégorie online de A',
        isEvent: false,
        conditionalFields: [],
        canBeDuo: false,
        canBeEducational: false,
        onlineOfflinePlatform: CATEGORY_STATUS.ONLINE,
        reimbursementRule: REIMBURSEMENT_RULES.STANDARD,
        isSelectable: true,
      },
      {
        id: 'A-B',
        categoryId: 'A',
        proLabel: 'Sous catégorie offline de A',
        isEvent: false,
        conditionalFields: [],
        canBeDuo: false,
        canBeEducational: false,
        onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
        reimbursementRule: REIMBURSEMENT_RULES.STANDARD,
        isSelectable: true,
      },
    ]

    const venue = {
      name: 'ma venue',
      publicName: 'ma venue (nom public)',
      isVirtual: true,
    }

    const stock = {
      quantity: null,
      price: 0,
      bookingLimitDatetime: null,
    }

    const offer = {
      id: 'AB',
      nonHumanizedId: 1,
      name: 'mon offre',
      description: 'ma description',
      categoryName: categories[0].proLabel,
      subCategoryName: subCategories[0].proLabel,
      subcategoryId: subCategories[0].id,
      accessibility: {
        visual: false,
        audio: false,
        motor: false,
        mental: false,
        none: true,
      },
      isDuo: false,
      author: 'jean-mich',
      stageDirector: 'jean-mich',
      speaker: 'jean-mich',
      visa: '0123',
      performer: 'jean-mich',
      isbn: '0123',
      durationMinutes: '01:00',
      url: 'https://offer-url.example.com',
      venueName: venue.name,
      venuePublicName: venue.publicName,
      isVenueVirtual: venue.isVirtual,
      offererName: 'mon offerer',
      bookingEmail: 'booking@example.com',
      externalTicketOfficeUrl: 'https://grand-public-url.example.com',
      withdrawalDetails: 'détails de retrait',
      withdrawalType: null,
      withdrawalDelay: null,
      status: OfferStatus.ACTIVE,
    }
    const preview = {
      offerData: {
        name: offer.name,
        description: offer.description,
        isEvent: false,
        isDuo: offer.isDuo,
      },
    }

    props = {
      offerId: offer.id,
      nonHumanizedOfferId: offer.nonHumanizedId,
      providerName: 'Ciné Office',
      offer: offer,
      stockThing: stock,
      stockEventList: undefined,
      subCategories: subCategories,
      preview: preview,
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

  describe('On edition', () => {
    it('should render component with informations', async () => {
      // given / when
      renderSummary({ props })

      // then
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

      expect(screen.getByText(props.offer.categoryName)).toBeInTheDocument()
      expect(screen.getByText(props.offer.subCategoryName)).toBeInTheDocument()
      expect(screen.getByText(props.offer.offererName)).toBeInTheDocument()
      expect(screen.getByText(props.offer.venuePublicName)).toBeInTheDocument()
      expect(
        screen.getByText(props.offer.withdrawalDetails)
      ).toBeInTheDocument()
      expect(screen.getByText(props.offer.url)).toBeInTheDocument()
      expect(
        screen.getByText(props.offer.externalTicketOfficeUrl)
      ).toBeInTheDocument()
      expect(screen.getByText('Non accessible')).toBeInTheDocument()
      expect(screen.getByText(props.offer.bookingEmail)).toBeInTheDocument()
      expect(screen.getByText('0 €')).toBeInTheDocument()
      expect(screen.getByText('Illimité')).toBeInTheDocument()
      expect(screen.getAllByText(props.offer.name)).toHaveLength(2)
      expect(screen.getAllByText(props.offer.description)).toHaveLength(2)
      expect(
        screen.getByText('Retour à la liste des offres')
      ).toBeInTheDocument()
      expect(screen.getByText('Visualiser dans l’app')).toBeInTheDocument()
    })
  })

  describe('On Creation', () => {
    beforeEach(() => {
      props.offer.status = OfferStatus.DRAFT
    })
    it('should render component with informations', async () => {
      // given / when
      renderSummary({
        props,
        url: generatePath(
          getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: 'AA' }
        ),
      })

      // then
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
      expect(screen.getByText(props.offer.categoryName)).toBeInTheDocument()
      expect(screen.getByText(props.offer.subCategoryName)).toBeInTheDocument()
      expect(screen.getByText(props.offer.offererName)).toBeInTheDocument()
      expect(screen.getByText(props.offer.venuePublicName)).toBeInTheDocument()
      expect(
        screen.getByText(props.offer.withdrawalDetails)
      ).toBeInTheDocument()
      expect(screen.getByText(props.offer.url)).toBeInTheDocument()
      expect(
        screen.getByText(props.offer.externalTicketOfficeUrl)
      ).toBeInTheDocument()
      expect(screen.getByText('Non accessible')).toBeInTheDocument()
      expect(screen.getByText(props.offer.bookingEmail)).toBeInTheDocument()
      expect(screen.getByText('0 €')).toBeInTheDocument()
      expect(screen.getByText('Illimité')).toBeInTheDocument()
      expect(screen.getAllByText(props.offer.name)).toHaveLength(2)
      expect(screen.getAllByText(props.offer.description)).toHaveLength(2)
      expect(
        screen.queryByText('Visualiser dans l’app')
      ).not.toBeInTheDocument()
    })

    describe('When it is form v3', () => {
      it('should render component with right buttons', async () => {
        // when
        renderSummary({
          props,
          url: generatePath(
            getOfferIndividualPath({
              step: OFFER_WIZARD_STEP_IDS.SUMMARY,
              mode: OFFER_WIZARD_MODE.CREATION,
            }),
            { offerId: 'AA' }
          ),
        })

        // then
        expect(screen.getByText('Étape précédente')).toBeInTheDocument()
        expect(
          screen.getByText('Sauvegarder le brouillon et quitter')
        ).toBeInTheDocument()
        expect(screen.getByText('Publier l’offre')).toBeInTheDocument()
      })

      it('should link to creation confirmation page', async () => {
        // when
        renderSummary({
          props,
          url: generatePath(
            getOfferIndividualPath({
              step: OFFER_WIZARD_STEP_IDS.SUMMARY,
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
    })

    it('should disabled publish button link during submit', async () => {
      // when
      renderSummary({
        props,
        url: generatePath(
          getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: 'AA' }
        ),
      })
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
        await screen.getByText('Confirmation page: creation')
      ).toBeInTheDocument()
    })

    it('should display notification on api error', async () => {
      // when
      renderSummary({
        props,
        url: generatePath(
          getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: 'AA' }
        ),
      })
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
      const notificationError = screen.getByTestId('global-notification-error')
      expect(notificationError).toBeInTheDocument()
      expect(notificationError.textContent).toBe(
        "Une erreur s'est produite, veuillez réessayer"
      )
    })

    it('should display redirect modal if first offer', async () => {
      jest.spyOn(useNewOfferCreationJourney, 'default').mockReturnValue(true)

      const context = contextValues
      context.venueId = 'AB'
      context.showVenuePopin = {
        AB: true,
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

      renderSummary({
        props,
        storeOverride,
        url: generatePath(
          getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.CREATION,
          }),
          { offerId: 'AA' }
        ),
        context,
      })

      await userEvent.click(
        screen.getByRole('button', { name: /Publier l’offre/ })
      )

      expect(
        await screen.getByText('Félicitations, vous avez créé votre offre !')
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
        renderSummary({ props, url })

        // then
        expect(screen.getByText('Vous y êtes presque !')).toBeInTheDocument()
      }
    )

    it('should display a notification when saving as draft', async () => {
      // when
      renderSummary({
        props,
        url: generatePath(
          getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
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
      // when
      renderSummary({
        props,
        url: generatePath(
          getOfferIndividualPath({
            step: OFFER_WIZARD_STEP_IDS.SUMMARY,
            mode: OFFER_WIZARD_MODE.EDITION,
          }),
          { offerId: 'AA' }
        ),
      })

      // then
      expect(
        screen.queryByText('Vous y êtes presque !')
      ).not.toBeInTheDocument()
    })
  })
})
