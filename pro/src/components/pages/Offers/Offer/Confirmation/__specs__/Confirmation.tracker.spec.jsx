import '@testing-library/jest-dom'

import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { api } from 'apiClient/api'
import * as useAnalytics from 'components/hooks/useAnalytics'
import { renderOffer } from 'components/pages/Offers/Offer/__specs__/render'
import { Events } from 'core/FirebaseEvents/constants'
import * as pcapi from 'repository/pcapi/pcapi'
import { offerFactory } from 'utils/apiFactories'

const mockLogEvent = jest.fn()

jest.mock('utils/config', () => {
  return {
    WEBAPP_URL: 'http://localhost',
  }
})

jest.mock('repository/pcapi/pcapi', () => ({
  updateOffersActiveStatus: jest.fn(),
  loadCategories: jest.fn(),
  getUserValidatedOfferersNames: jest.fn(),
  getVenuesForOfferer: jest.fn(),
  getOfferer: jest.fn(),
}))

describe('confirmation page', () => {
  it('should track when click on offer creation button', async () => {
    // Given
    const categories = {
      categories: [
        {
          id: 'ID',
          name: 'Musique',
          proLabel: 'Musique',
          appLabel: 'Musique',
          isSelectable: true,
        },
      ],
      subcategories: [
        {
          id: 'ID',
          name: 'Musique SubCat 1',
          categoryId: 'ID',
          isEvent: false,
          isDigital: false,
          isDigitalDeposit: false,
          isPhysicalDeposit: true,
          proLabel: 'Musique SubCat 1',
          appLabel: 'Musique SubCat 1',
          conditionalFields: ['author', 'musicType', 'performer'],
          canExpire: true,
          canBeDuo: false,
          isSelectable: true,
        },
      ],
    }
    pcapi.loadCategories.mockResolvedValue(categories)
    const offer = offerFactory({
      name: 'mon offre',
      status: 'DRAFT',
      venueId: 'VENUEID',
    })
    jest.spyOn(api, 'getOffer').mockResolvedValue(offer)
    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
    pcapi.getVenuesForOfferer.mockResolvedValue([
      { id: 'AB', publicName: 'venue', name: 'venue' },
    ])
    pcapi.getUserValidatedOfferersNames.mockResolvedValue([])

    // When
    await renderOffer({
      pathname: `/offre/${offer.id}/individuel/creation/confirmation`,
    })

    // Then
    await userEvent.click(screen.getByText('Créer une nouvelle offre'))
    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'confirmation',
        isEdition: false,
        to: 'details',
        used: 'ConfirmationButton',
      }
    )
  })
})
