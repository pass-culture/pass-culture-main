import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import fetchMock from 'jest-fetch-mock'
import React from 'react'

import { api } from 'apiClient/api'
import {
  CategoriesResponseModel,
  CollectiveOfferResponseIdModel,
  EducationalDomainsResponseModel,
  GetEducationalOfferersResponseModel,
  GetVenueResponseModel,
} from 'apiClient/v1'
import {
  Events,
  OFFER_FROM_TEMPLATE_ENTRIES,
} from 'core/FirebaseEvents/constants'
import {
  CollectiveOffer,
  CollectiveOfferTemplate,
  EducationalCategories,
  Mode,
} from 'core/OfferEducational'
import * as useAnalytics from 'hooks/useAnalytics'
import {
  categoriesFactory,
  subCategoriesFactory,
} from 'screens/OfferEducational/__tests-utils__'
import { collectiveOfferTemplateFactory } from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import CollectiveOfferSummaryEdition from '../CollectiveOfferSummaryEdition'

const renderCollectiveOfferSummaryEdition = (
  offer: CollectiveOfferTemplate | CollectiveOffer,
  categories: EducationalCategories
) => {
  const storeOverrides = {
    user: {
      initialized: true,
      currentUser: {
        firstName: 'John',
        dateCreated: '2022-07-29T12:18:43.087097Z',
        email: 'john@do.net',
        id: '1',
        nonHumanizedId: '1',
        isAdmin: false,
        isEmailValidated: true,
        roles: [],
      },
    },
  }

  renderWithProviders(
    <CollectiveOfferSummaryEdition
      offer={offer}
      categories={categories}
      reloadCollectiveOffer={jest.fn()}
      mode={Mode.EDITION}
    />,
    { storeOverrides }
  )
}

describe('CollectiveOfferSummary', () => {
  let offer: CollectiveOfferTemplate | CollectiveOffer
  let categories: EducationalCategories
  const mockLogEvent = jest.fn()

  beforeEach(() => {
    offer = collectiveOfferTemplateFactory({ isTemplate: true })
    categories = {
      educationalCategories: categoriesFactory([{ id: 'CAT_1' }]),
      educationalSubCategories: subCategoriesFactory([
        { categoryId: 'CAT_1', id: 'SUBCAT_1' },
      ]),
    }
    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
    jest.spyOn(api, 'getVenue').mockResolvedValue({} as GetVenueResponseModel)
    jest.spyOn(api, 'getCollectiveOfferTemplate').mockResolvedValue(offer)
    jest
      .spyOn(api, 'getCategories')
      .mockResolvedValue({} as CategoriesResponseModel)
    jest
      .spyOn(api, 'listEducationalOfferers')
      .mockResolvedValue({} as GetEducationalOfferersResponseModel)
    jest
      .spyOn(api, 'listEducationalDomains')
      .mockResolvedValue({} as EducationalDomainsResponseModel)

    jest
      .spyOn(api, 'createCollectiveOffer')
      .mockResolvedValue({} as CollectiveOfferResponseIdModel)
    fetchMock.mockIf(/image.jpg/, 'some response')
  })

  it('should display desactive offer option when offer is active and not booked', () => {
    offer = collectiveOfferTemplateFactory({ isTemplate: true, isActive: true })
    renderCollectiveOfferSummaryEdition(offer, categories)

    const desactivateOffer = screen.getByRole('button', {
      name: 'Masquer la publication sur Adage',
    })

    expect(desactivateOffer).toBeInTheDocument()
  })

  it('should log event when clicking duplicate offer button', async () => {
    offer = collectiveOfferTemplateFactory({ isTemplate: true, isActive: true })
    renderCollectiveOfferSummaryEdition(offer, categories)

    const duplicateOffer = screen.getByRole('button', {
      name: 'Créer une offre réservable pour un établissement scolaire',
    })
    await userEvent.click(duplicateOffer)

    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_DUPLICATE_TEMPLATE_OFFER,
      {
        from: OFFER_FROM_TEMPLATE_ENTRIES.OFFER_TEMPLATE_RECAP,
      }
    )
  })
})
