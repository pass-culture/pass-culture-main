import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { generatePath, Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import {
  GetIndividualOfferResponseModel,
  OfferStatus,
  WithdrawalTypeEnum,
} from 'apiClient/v1'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferBreadcrumb/constants'
import Notification from 'components/Notification/Notification'
import {
  IndividualOfferContext,
  IndividualOfferContextValues,
} from 'context/IndividualOfferContext'
import { REIMBURSEMENT_RULES } from 'core/Finances'
import { Events } from 'core/FirebaseEvents/constants'
import { CATEGORY_STATUS, OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { IndividualOffer, OfferSubCategory } from 'core/Offers/types'
import { getIndividualOfferPath } from 'core/Offers/utils/getIndividualOfferUrl'
import { AccessiblityEnum } from 'core/shared'
import { IndividualOfferVenueItem } from 'core/Venue/types'
import * as useAnalytics from 'hooks/useAnalytics'
import { ButtonLink } from 'ui-kit'
import {
  individualOfferCategoryFactory,
  individualOfferContextFactory,
  individualOfferFactory,
  individualOfferSubCategoryFactory,
  individualOfferVenueItemFactory,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import InformationsScreen, {
  InformationsScreenProps,
} from '../InformationsScreen'

const mockLogEvent = vi.fn()

vi.mock('screens/IndividualOffer/Informations/utils', () => {
  return {
    filterCategories: vi.fn(),
  }
})

vi.mock('repository/pcapi/pcapi', () => ({
  postThumbnail: vi.fn(),
}))

const renderInformationsScreen = (
  props: InformationsScreenProps,
  contextOverride: IndividualOfferContextValues,
  url = generatePath(
    getIndividualOfferPath({
      step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
      mode: OFFER_WIZARD_MODE.CREATION,
    }),
    { offerId: 'AA' }
  )
) => {
  const storeOverrides = {
    user: {
      initialized: true,
      currentUser: {
        isAdmin: false,
        email: 'email@example.com',
      },
    },
  }
  const contextValue = individualOfferContextFactory(contextOverride)

  return renderWithProviders(
    <>
      <Routes>
        {Object.values(OFFER_WIZARD_MODE).map(mode => (
          <Route
            key={mode}
            path={getIndividualOfferPath({
              step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
              mode,
            })}
            element={
              <IndividualOfferContext.Provider value={contextValue}>
                <InformationsScreen {...props} />
                <ButtonLink link={{ to: '/outside', isExternal: false }}>
                  Go outside !
                </ButtonLink>
                <ButtonLink link={{ to: '/stocks', isExternal: false }}>
                  Go to stocks !
                </ButtonLink>
              </IndividualOfferContext.Provider>
            }
          />
        ))}
        <Route
          path={getIndividualOfferPath({
            step: OFFER_WIZARD_STEP_IDS.STOCKS,
            mode: OFFER_WIZARD_MODE.CREATION,
          })}
          element={<div>There is the stock route content</div>}
        />
        <Route
          path="/outside"
          element={<div>This is outside offer creation</div>}
        />
      </Routes>
      <Notification />
    </>,
    { storeOverrides, initialRouterEntries: [url] }
  )
}

const scrollIntoViewMock = vi.fn()

describe('screens:IndividualOffer::Informations::creation', () => {
  let props: InformationsScreenProps
  let contextOverride: IndividualOfferContextValues
  let offer: IndividualOffer
  const offerId = 12

  beforeEach(() => {
    Element.prototype.scrollIntoView = scrollIntoViewMock
    offer = individualOfferFactory({
      id: offerId,
      author: 'Offer author',
      bookingEmail: 'booking@email.com',
      description: 'Offer description',
      durationMinutes: 140,
      isActive: true,
      isDuo: false,
      isEvent: true,
      isDigital: false,
      accessibility: {
        [AccessiblityEnum.AUDIO]: true,
        [AccessiblityEnum.MENTAL]: true,
        [AccessiblityEnum.MOTOR]: true,
        [AccessiblityEnum.VISUAL]: true,
        [AccessiblityEnum.NONE]: false,
      },
      isNational: false,
      name: 'Offer name',
      musicSubType: '',
      musicType: '',
      offererId: 12,
      offererName: '',
      performer: 'Offer performer',
      ean: '',
      showSubType: '',
      showType: '',
      stageDirector: 'Offer stageDirector',
      speaker: 'Offer speaker',
      subcategoryId: 'physical',
      image: undefined,
      url: 'https://offer.example.com',
      externalTicketOfficeUrl: 'https://external.example.com',
      venueId: 1,
      venue: {
        id: 1,
        name: 'Venue name',
        publicName: 'Venue publicName',
        isVirtual: false,
        address: '15 rue de la corniche',
        postalCode: '75001',
        city: 'Paris',
        offerer: {
          id: 1,
          name: 'Offerer name',
        },
        departmentCode: '75',
        accessibility: {
          [AccessiblityEnum.AUDIO]: false,
          [AccessiblityEnum.MENTAL]: false,
          [AccessiblityEnum.MOTOR]: false,
          [AccessiblityEnum.VISUAL]: false,
          [AccessiblityEnum.NONE]: true,
        },
      },
      visa: '',
      withdrawalDetails: 'Offer withdrawalDetails',
      withdrawalDelay: 140,
      withdrawalType: WithdrawalTypeEnum.ON_SITE,
      stocks: [],
      lastProviderName: null,
      lastProvider: null,
      status: OfferStatus.DRAFT,
    })

    const categories = [
      individualOfferCategoryFactory({
        id: 'A',
        proLabel: 'Catégorie A',
        isSelectable: true,
      }),
      // we need two categories otherwise the first one is preselected and the form is dirty
      individualOfferCategoryFactory({
        id: 'B',
        proLabel: 'Catégorie B',
        isSelectable: true,
      }),
    ]
    const subCategories: OfferSubCategory[] = [
      individualOfferSubCategoryFactory({
        id: 'virtual',
        categoryId: 'A',
        proLabel: 'Sous catégorie online de A',
        isEvent: false,
        conditionalFields: [],
        canBeDuo: false,
        canBeEducational: false,
        canBeWithdrawable: false,
        onlineOfflinePlatform: CATEGORY_STATUS.ONLINE,
        reimbursementRule: REIMBURSEMENT_RULES.STANDARD,
        isSelectable: true,
      }),
      individualOfferSubCategoryFactory({
        id: 'physical',
        categoryId: 'A',
        proLabel: 'Sous catégorie offline de A',
        isEvent: false,
        conditionalFields: [],
        canBeDuo: true,
        canBeEducational: false,
        canBeWithdrawable: false,
        onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
        reimbursementRule: REIMBURSEMENT_RULES.STANDARD,
        isSelectable: true,
      }),
      individualOfferSubCategoryFactory({
        id: 'physicalB',
        categoryId: 'B',
        proLabel: 'Sous catégorie offline de B',
        isEvent: false,
        conditionalFields: [],
        canBeDuo: true,
        canBeEducational: false,
        canBeWithdrawable: false,
        onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
        reimbursementRule: REIMBURSEMENT_RULES.STANDARD,
        isSelectable: true,
      }),
    ]

    const venue1: IndividualOfferVenueItem = individualOfferVenueItemFactory()
    const venue2: IndividualOfferVenueItem = individualOfferVenueItemFactory({
      isVirtual: true,
    })

    contextOverride = individualOfferContextFactory({
      venueList: [venue1, venue2],
      offererNames: [{ id: 1, name: 'mon offerer A' }],
      categories,
      subCategories,
      offer: null,
    })

    props = {
      venueId: offer.venue.id.toString(),
      offererId: offer.venue.offerer.id.toString(),
    }

    vi.spyOn(api, 'getOffer').mockResolvedValue(
      {} as GetIndividualOfferResponseModel
    )
    vi.spyOn(api, 'postOffer').mockResolvedValue({
      id: offerId,
    } as GetIndividualOfferResponseModel)
    vi.spyOn(api, 'patchOffer').mockResolvedValue({
      id: offerId,
    } as GetIndividualOfferResponseModel)
    vi.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
  })

  it('should not block when from has not be touched', async () => {
    renderInformationsScreen(props, contextOverride)

    await userEvent.click(screen.getByText('Go outside !'))

    expect(
      screen.getByText('This is outside offer creation')
    ).toBeInTheDocument()
  })

  it('should block when form has just been touched', async () => {
    renderInformationsScreen(props, contextOverride)

    const categorySelect = screen.getByLabelText('Catégorie')
    await userEvent.selectOptions(categorySelect, 'A')

    await userEvent.click(screen.getByText('Go outside !'))

    expect(
      screen.getByText(
        'Restez sur la page et cliquez sur “Sauvegarder le brouillon” pour ne rien perdre de vos modifications.'
      )
    ).toBeInTheDocument()
  })

  it('should not block when submitting minimal physical offer from action bar', async () => {
    renderInformationsScreen(props, contextOverride)

    const categorySelect = screen.getByLabelText('Catégorie')
    await userEvent.selectOptions(categorySelect, 'A')
    const subCategorySelect = screen.getByLabelText('Sous-catégorie')
    await userEvent.selectOptions(subCategorySelect, 'physical')
    const nameField = screen.getByLabelText('Titre de l’offre')
    await userEvent.type(nameField, 'Le nom de mon offre')

    await userEvent.click(screen.getByText('Étape suivante'))

    expect(
      await screen.findByText('There is the stock route content')
    ).toBeInTheDocument()
  })

  it('should not block the user when saving draft from action bar', async () => {
    // FIX ME: at first I wanna tested that user could aftewards go outside
    // but I'm not able to do it, in test the form remain dirty
    // I don't figure why, maybe because of api mocks
    renderInformationsScreen(props, contextOverride)

    const categorySelect = screen.getByLabelText('Catégorie')
    await userEvent.selectOptions(categorySelect, 'A')
    const subCategorySelect = screen.getByLabelText('Sous-catégorie')
    await userEvent.selectOptions(subCategorySelect, 'physical')
    const nameField = screen.getByLabelText('Titre de l’offre')
    await userEvent.type(nameField, 'Le nom de mon offre')

    await userEvent.click(screen.getByText('Sauvegarder le brouillon'))

    expect(api.postOffer).toHaveBeenCalledTimes(1)
    expect(
      screen.getByText(
        'Tous les champs sont obligatoires sauf mention contraire.'
      )
    ).toBeInTheDocument()
  })

  it('should track with offerId when offer has been created', async () => {
    contextOverride.offer = offer
    renderInformationsScreen(props, contextOverride)

    const categorySelect = screen.getByLabelText('Catégorie')
    await userEvent.selectOptions(categorySelect, 'A')
    const subCategorySelect = screen.getByLabelText('Sous-catégorie')
    await userEvent.selectOptions(subCategorySelect, 'physical')
    const nameField = screen.getByLabelText('Titre de l’offre')
    await userEvent.type(nameField, 'Le nom de mon offre')

    await userEvent.click(screen.getByText('Sauvegarder le brouillon'))
    // FIX ME: this test seems strange why is patched called and not post ?
    expect(api.patchOffer).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'informations',
        isDraft: true,
        isEdition: false,
        offerId: offerId,
        subcategoryId: 'physical',
        to: 'informations',
        used: 'DraftButtons',
      }
    )
  })
})
