import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'
import { generatePath, Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import { GetIndividualOfferResponseModel } from 'apiClient/v1'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import Notification from 'components/Notification/Notification'
import {
  IndividualOfferContext,
  IndividualOfferContextValues,
} from 'context/IndividualOfferContext'
import { CATEGORY_STATUS, OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { IndividualOffer } from 'core/Offers/types'
import { getIndividualOfferPath } from 'core/Offers/utils/getIndividualOfferUrl'
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
    offer = individualOfferFactory()

    const categories = [
      individualOfferCategoryFactory({ id: 'A' }),
      // we need two categories otherwise the first one is preselected and the form is dirty
      individualOfferCategoryFactory({ id: 'B' }),
    ]
    const subCategories = [
      individualOfferSubCategoryFactory({
        id: 'virtual',
        categoryId: 'A',
        onlineOfflinePlatform: CATEGORY_STATUS.ONLINE,
      }),
      individualOfferSubCategoryFactory({
        id: 'physical',
        categoryId: 'A',
        onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
      }),
      individualOfferSubCategoryFactory({
        id: 'physicalB',
        categoryId: 'B',
        onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
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
      offererId: offer.venue.managingOfferer.id.toString(),
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
      screen.getByText('Les informations non enregistrées seront perdues')
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

    await userEvent.click(screen.getByText('Enregistrer et continuer'))

    expect(
      await screen.findByText('There is the stock route content')
    ).toBeInTheDocument()
  })
})
