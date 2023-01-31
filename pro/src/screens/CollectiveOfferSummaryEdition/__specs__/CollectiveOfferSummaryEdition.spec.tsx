import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { api } from 'apiClient/api'
import {
  Events,
  OFFER_FROM_TEMPLATE_ENTRIES,
} from 'core/FirebaseEvents/constants'
import {
  CollectiveOffer,
  CollectiveOfferTemplate,
  EducationalCategories,
} from 'core/OfferEducational'
import * as useAnalytics from 'hooks/useAnalytics'
import {
  categoriesFactory,
  subCategoriesFactory,
} from 'screens/OfferEducational/__tests-utils__'
import {
  collectiveStockFactory,
  collectiveOfferTemplateFactory,
  collectiveOfferFactory,
} from 'utils/collectiveApiFactories'
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
  })

  it('should display desactive offer option when offer is active and not booked', () => {
    offer = collectiveOfferTemplateFactory({ isTemplate: true, isActive: true })
    renderCollectiveOfferSummaryEdition(offer, categories)

    const desactivateOffer = screen.getByRole('button', {
      name: 'Masquer la publication sur Adage',
    })

    expect(desactivateOffer).toBeInTheDocument()
  })

  it('should display cancel booking button when offer is booked', () => {
    offer = collectiveOfferFactory({
      isTemplate: false,
      isActive: true,
      collectiveStock: collectiveStockFactory({ isBooked: true }),
    })
    renderCollectiveOfferSummaryEdition(offer, categories)

    const cancelBooking = screen.getByRole('button', {
      name: 'Annuler la réservation',
    })

    expect(cancelBooking).toBeInTheDocument()
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

  it('should activate offer', async () => {
    offer = collectiveOfferTemplateFactory({
      isTemplate: true,
      isActive: false,
    })
    renderCollectiveOfferSummaryEdition(offer, categories)
    const toggle = jest
      .spyOn(api, 'patchCollectiveOffersTemplateActiveStatus')
      .mockResolvedValue()

    const activateOffer = screen.getByRole('button', {
      name: 'Publier sur Adage',
    })

    await userEvent.click(activateOffer)

    expect(toggle).toHaveBeenCalledTimes(1)

    const desactivateOffer = screen.getByRole('button', {
      name: 'Masquer la publication sur Adage',
    })

    expect(desactivateOffer).toBeInTheDocument()
  })
})
