import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import {
  ApiError,
  GetIndividualOfferResponseModel,
  SubcategoryResponseModel,
} from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import Notification from 'components/Notification/Notification'
import {
  IndividualOfferContext,
  IndividualOfferContextValues,
} from 'context/IndividualOfferContext'
import { CATEGORY_STATUS, OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { getIndividualOfferPath } from 'core/Offers/utils/getIndividualOfferUrl'
import { IndividualOfferVenueItem } from 'core/Venue/types'
import * as pcapi from 'repository/pcapi/pcapi'
import {
  individualOfferCategoryFactory,
  individualOfferContextFactory,
  individualOfferSubCategoryFactory,
  individualOfferVenueItemFactory,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import InformationsScreen, {
  InformationsScreenProps,
} from '../InformationsScreen'

vi.mock('screens/IndividualOffer/Informations/utils', () => {
  return {
    filterCategories: vi.fn(),
  }
})

vi.mock('utils/windowMatchMedia', () => ({
  doesUserPreferReducedMotion: vi.fn(() => true),
}))

vi.mock('repository/pcapi/pcapi', () => ({
  postThumbnail: vi.fn(),
}))

const renderInformationsScreen = (
  props: InformationsScreenProps,
  contextOverride: IndividualOfferContextValues,
  searchParam = ''
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
        <Route
          path={getIndividualOfferPath({
            step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
            mode: OFFER_WIZARD_MODE.CREATION,
          })}
          element={
            <IndividualOfferContext.Provider value={contextValue}>
              <InformationsScreen {...props} />
            </IndividualOfferContext.Provider>
          }
        />
        <Route
          path={getIndividualOfferPath({
            step: OFFER_WIZARD_STEP_IDS.STOCKS,
            mode: OFFER_WIZARD_MODE.CREATION,
          })}
          element={<div>There is the stock route content</div>}
        />
      </Routes>
      <Notification />
    </>,
    {
      storeOverrides,
      initialRouterEntries: [
        getIndividualOfferPath({
          step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
          mode: OFFER_WIZARD_MODE.CREATION,
        }) + searchParam,
      ],
    }
  )
}

const scrollIntoViewMock = vi.fn()

describe('screens:IndividualOffer::Informations::creation', () => {
  let props: InformationsScreenProps
  let contextOverride: IndividualOfferContextValues
  const offererId = 1
  const offerId = 5

  beforeEach(() => {
    Element.prototype.scrollIntoView = scrollIntoViewMock
    const categories = [individualOfferCategoryFactory({ id: 'A' })]
    const subCategories: SubcategoryResponseModel[] = [
      individualOfferSubCategoryFactory({
        id: 'virtual',
        categoryId: 'A',
        isEvent: false,
        onlineOfflinePlatform: CATEGORY_STATUS.ONLINE,
        isSelectable: true,
      }),
      individualOfferSubCategoryFactory({
        id: 'physical',
        categoryId: 'A',
        isEvent: false,
        canBeDuo: true,
        onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
      }),
    ]

    const venue1: IndividualOfferVenueItem = individualOfferVenueItemFactory({
      id: 1,
    })
    const venue2: IndividualOfferVenueItem = individualOfferVenueItemFactory({
      id: 2,
      isVirtual: true,
    })

    contextOverride = individualOfferContextFactory({
      venueList: [venue1, venue2],
      offererNames: [{ id: offererId, name: 'mon offerer A' }],
      categories,
      subCategories,
      offer: null,
    })

    props = {
      offererId: offererId.toString(),
      venueId: venue1.id.toString(),
    }

    vi.spyOn(api, 'postOffer').mockResolvedValue({
      id: offerId,
    } as GetIndividualOfferResponseModel)
  })

  it('should submit minimal physical offer', async () => {
    renderInformationsScreen(props, contextOverride)

    const categorySelect = await screen.findByLabelText('Catégorie *')
    await userEvent.selectOptions(categorySelect, 'A')
    const subCategorySelect = screen.getByLabelText('Sous-catégorie *')
    await userEvent.selectOptions(subCategorySelect, 'physical')
    const nameField = screen.getByLabelText('Titre de l’offre *')
    await userEvent.type(nameField, 'Le nom de mon offre')

    await userEvent.click(await screen.findByText('Enregistrer et continuer'))

    expect(api.postOffer).toHaveBeenCalledTimes(1)
    expect(api.postOffer).toHaveBeenCalledWith({
      audioDisabilityCompliant: true,
      bookingEmail: null,
      bookingContact: null,
      description: null,
      durationMinutes: null,
      externalTicketOfficeUrl: null,
      extraData: {},
      isDuo: true,
      isNational: false,
      mentalDisabilityCompliant: true,
      motorDisabilityCompliant: true,
      name: 'Le nom de mon offre',
      subcategoryId: 'physical',
      url: null,
      venueId: 1,
      visualDisabilityCompliant: true,
      withdrawalDelay: null,
      withdrawalDetails: null,
      withdrawalType: null,
    })
    expect(
      await screen.findByText('There is the stock route content')
    ).toBeInTheDocument()
    expect(pcapi.postThumbnail).not.toHaveBeenCalled()
  })

  it('should display api errors', async () => {
    renderInformationsScreen(props, contextOverride)

    const categorySelect = await screen.findByLabelText('Catégorie *')
    await userEvent.selectOptions(categorySelect, 'A')
    const subCategorySelect = screen.getByLabelText('Sous-catégorie *')
    await userEvent.selectOptions(subCategorySelect, 'physical')
    const nameField = screen.getByLabelText('Titre de l’offre *')
    await userEvent.type(nameField, 'Le nom de mon offre')

    vi.spyOn(api, 'postOffer').mockRejectedValue(
      new ApiError(
        {} as ApiRequestOptions,
        {
          status: 500,
          body: {
            name: 'api wrong name',
            venue: 'api wrong venue',
          },
        } as ApiResult,
        ''
      )
    )
    const nextButton = screen.getByText('Enregistrer et continuer')

    await userEvent.click(screen.getByText('Enregistrer et continuer'))

    expect(api.postOffer).toHaveBeenCalledTimes(1)
    expect(pcapi.postThumbnail).not.toHaveBeenCalled()
    expect(await screen.findByText('api wrong name')).toBeInTheDocument()
    expect(screen.getByText('api wrong venue')).toBeInTheDocument()
    expect(nextButton).not.toBeDisabled()
  })

  it('should submit minimal virtual offer', async () => {
    // Use virtual venue
    props.venueId = '2'
    renderInformationsScreen(props, contextOverride)

    const categorySelect = await screen.findByLabelText('Catégorie *')
    await userEvent.selectOptions(categorySelect, 'A')
    const subCategorySelect = screen.getByLabelText('Sous-catégorie *')
    await userEvent.selectOptions(subCategorySelect, 'virtual')

    const nameField = screen.getByLabelText('Titre de l’offre *')
    await userEvent.type(nameField, 'Le nom de mon offre')

    const urlField = await screen.findByLabelText('URL d’accès à l’offre *')

    await userEvent.type(urlField, 'https://example.com/')

    await userEvent.click(await screen.findByText('Enregistrer et continuer'))

    expect(api.postOffer).toHaveBeenCalledTimes(1)
    expect(api.postOffer).toHaveBeenCalledWith({
      audioDisabilityCompliant: true,
      bookingEmail: null,
      bookingContact: null,
      description: null,
      durationMinutes: null,
      externalTicketOfficeUrl: null,
      extraData: {},
      isDuo: false,
      isNational: false,
      mentalDisabilityCompliant: true,
      motorDisabilityCompliant: true,
      name: 'Le nom de mon offre',
      subcategoryId: 'virtual',
      url: 'https://example.com/',
      venueId: 2,
      visualDisabilityCompliant: true,
      withdrawalDelay: null,
      withdrawalDetails: null,
      withdrawalType: null,
    })
    expect(
      await screen.findByText('There is the stock route content')
    ).toBeInTheDocument()
    expect(pcapi.postThumbnail).not.toHaveBeenCalled()
  })

  it('should submit offer when several offerer and offer type set', async () => {
    const categories = [individualOfferCategoryFactory({ id: 'A' })]
    const subCategories: SubcategoryResponseModel[] = [
      individualOfferSubCategoryFactory({
        id: 'virtual',
        categoryId: 'A',
        isEvent: false,
        onlineOfflinePlatform: CATEGORY_STATUS.ONLINE,
        isSelectable: true,
      }),
      individualOfferSubCategoryFactory({
        id: 'physical',
        categoryId: 'A',
        isEvent: false,
        canBeDuo: true,
        onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
      }),
    ]
    const offererId1 = 1
    const offererId2 = 2
    const venue1Offerer1: IndividualOfferVenueItem =
      individualOfferVenueItemFactory({
        id: 1,
        managingOffererId: offererId1,
      })
    const venue2Offerer1: IndividualOfferVenueItem =
      individualOfferVenueItemFactory({
        id: 2,
        isVirtual: true,
        managingOffererId: offererId1,
      })
    const venue1Offerer2: IndividualOfferVenueItem =
      individualOfferVenueItemFactory({
        id: 3,
        managingOffererId: offererId2,
      })
    const venue2Offerer2: IndividualOfferVenueItem =
      individualOfferVenueItemFactory({
        id: 4,
        isVirtual: true,
        managingOffererId: offererId2,
      })

    const contextOverride = individualOfferContextFactory({
      venueList: [
        venue1Offerer1,
        venue2Offerer1,
        venue1Offerer2,
        venue2Offerer2,
      ],
      offererNames: [
        { id: offererId1, name: 'mon offerer A' },
        { id: offererId2, name: 'mon offerer B' },
      ],
      categories,
      subCategories,
      offer: null,
    })
    props = {
      offererId: offererId1.toString(),
      venueId: '',
    }
    const searchParam = '?offer-type=VIRTUAL_GOOD'
    renderInformationsScreen(props, contextOverride, searchParam)

    const categorySelect = await screen.findByLabelText('Catégorie *')
    await userEvent.selectOptions(categorySelect, 'A')
    const subCategorySelect = screen.getByLabelText('Sous-catégorie *')
    await userEvent.selectOptions(subCategorySelect, 'virtual')

    const nameField = screen.getByLabelText('Titre de l’offre *')
    await userEvent.type(nameField, 'Le nom de mon offre')
    const urlField = await screen.findByLabelText('URL d’accès à l’offre *')

    await userEvent.type(urlField, 'https://example.com/')

    await userEvent.click(await screen.findByText('Enregistrer et continuer'))

    expect(api.postOffer).toHaveBeenCalledTimes(1)
    expect(
      await screen.findByText('There is the stock route content')
    ).toBeInTheDocument()
  })
})
