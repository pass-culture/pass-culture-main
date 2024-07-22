import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'
import { generatePath, Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import {
  GetIndividualOfferResponseModel,
  VenueListItemResponseModel,
} from 'apiClient/v1'
import * as useAnalytics from 'app/App/analytics/firebase'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { Notification } from 'components/Notification/Notification'
import {
  IndividualOfferContext,
  IndividualOfferContextValues,
} from 'context/IndividualOfferContext/IndividualOfferContext'
import { CATEGORY_STATUS, OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { getIndividualOfferPath } from 'core/Offers/utils/getIndividualOfferUrl'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import {
  getIndividualOfferFactory,
  categoryFactory,
  individualOfferContextValuesFactory,
  subcategoryFactory,
  venueListItemFactory,
  getOffererNameFactory,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

import {
  InformationsScreen,
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
  const contextValue = individualOfferContextValuesFactory(contextOverride)

  return renderWithProviders(
    <>
      <Routes>
        {Object.values(OFFER_WIZARD_MODE).map((mode) => (
          <Route
            key={mode}
            path={getIndividualOfferPath({
              step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
              mode,
            })}
            element={
              <IndividualOfferContext.Provider value={contextValue}>
                <InformationsScreen {...props} />
                <ButtonLink to="/outside">Go outside !</ButtonLink>
                <ButtonLink to="/stocks">Go to stocks !</ButtonLink>
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
    { user: sharedCurrentUserFactory(), initialRouterEntries: [url] }
  )
}

const scrollIntoViewMock = vi.fn()

describe('screens:IndividualOffer::Informations::creation', () => {
  let props: InformationsScreenProps
  let contextOverride: IndividualOfferContextValues
  let offer: GetIndividualOfferResponseModel
  const offerId = 12

  beforeEach(() => {
    Element.prototype.scrollIntoView = scrollIntoViewMock
    offer = getIndividualOfferFactory()

    const categories = [
      categoryFactory({ id: 'A' }),
      // we need two categories otherwise the first one is preselected and the form is dirty
      categoryFactory({ id: 'B' }),
    ]
    const subCategories = [
      subcategoryFactory({
        id: 'virtual',
        categoryId: 'A',
        onlineOfflinePlatform: CATEGORY_STATUS.ONLINE,
      }),
      subcategoryFactory({
        id: 'physical',
        categoryId: 'A',
        onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
      }),
      subcategoryFactory({
        id: 'physicalB',
        categoryId: 'B',
        onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
      }),
    ]

    const venue1: VenueListItemResponseModel = venueListItemFactory()
    const venue2: VenueListItemResponseModel = venueListItemFactory({
      isVirtual: true,
    })

    contextOverride = individualOfferContextValuesFactory({
      categories,
      subCategories,
      offer: null,
    })

    props = {
      venueId: offer.venue.id.toString(),
      offererId: offer.venue.managingOfferer.id.toString(),
      venueList: [venue1, venue2],
      offererNames: [
        getOffererNameFactory({
          id: 1,
          name: 'mon offerer A',
        }),
      ],
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
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
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

    const categorySelect = screen.getByLabelText('Catégorie *')
    await userEvent.selectOptions(categorySelect, 'A')

    await userEvent.click(screen.getByText('Go outside !'))

    expect(
      screen.getByText('Les informations non enregistrées seront perdues')
    ).toBeInTheDocument()
  })

  it('should not block when submitting minimal physical offer from action bar', async () => {
    renderInformationsScreen(props, contextOverride)

    const categorySelect = screen.getByLabelText('Catégorie *')
    await userEvent.selectOptions(categorySelect, 'A')
    const subCategorySelect = screen.getByLabelText('Sous-catégorie *')
    await userEvent.selectOptions(subCategorySelect, 'physical')
    const nameField = screen.getByLabelText('Titre de l’offre *')
    await userEvent.type(nameField, 'Le nom de mon offre')

    await userEvent.click(screen.getByText('Enregistrer et continuer'))

    expect(
      await screen.findByText('There is the stock route content')
    ).toBeInTheDocument()
  })
})
