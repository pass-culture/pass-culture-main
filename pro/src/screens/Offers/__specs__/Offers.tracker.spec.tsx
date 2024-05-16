import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from 'apiClient/api'
import { UserRole } from 'apiClient/v1'
import { DEFAULT_SEARCH_FILTERS } from 'core/Offers/constants'
import { Audience } from 'core/shared/types'
import {
  defaultGetOffererResponseModel,
  getOfferManagingOffererFactory,
  getOffererNameFactory,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

import { Offers, OffersProps } from '../Offers'

const renderOffers = (props: OffersProps) =>
  renderWithProviders(<Offers {...props} />, {
    storeOverrides: {
      user: {
        selectedOffererId: defaultGetOffererResponseModel.id,
        currentUser: sharedCurrentUserFactory(),
      },
    },
  })

vi.mock('apiClient/api', () => ({
  api: {
    listOfferersNames: vi.fn(),
  },
}))

describe('tracker screen Offers', () => {
  it('should track when clciking on offer link', async () => {
    // Given
    const props = {
      currentPageNumber: 1,
      isLoading: false,
      currentUser: {
        isAdmin: false,
        roles: [UserRole.PRO],
      },
      loadAndUpdateOffers: vi.fn(),
      offerer: { ...defaultGetOffererResponseModel },
      offers: [],
      setIsLoading: vi.fn(),
      setOfferer: vi.fn(),
      urlSearchFilters: DEFAULT_SEARCH_FILTERS,
      separateIndividualAndCollectiveOffers: false,
      initialSearchFilters: DEFAULT_SEARCH_FILTERS,
      audience: Audience.INDIVIDUAL,
      redirectWithUrlFilters: vi.fn(),
      venues: [],
      categories: [],
    }

    const individualOffererNames = getOfferManagingOffererFactory()
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: [
        getOffererNameFactory({ ...individualOffererNames, id: 1 }),
      ],
    })

    renderOffers(props)

    await waitFor(() => {
      expect(screen.getByText('Créer une offre')).toBeInTheDocument()
    })
    expect(api.listOfferersNames).toHaveBeenCalledTimes(1)
    expect(api.listOfferersNames).toHaveBeenCalledWith(undefined, true)

    const createLink = screen.getByText('Créer une offre')
    await userEvent.click(createLink)
  })
})
