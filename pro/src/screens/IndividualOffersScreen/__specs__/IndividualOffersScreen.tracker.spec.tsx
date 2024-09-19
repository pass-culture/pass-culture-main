import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from 'apiClient/api'
import { UserRole } from 'apiClient/v1'
import { DEFAULT_SEARCH_FILTERS } from 'core/Offers/constants'
import { Audience } from 'core/shared/types'
import {
  defaultGetOffererResponseModel,
  getOffererNameFactory,
  getOfferManagingOffererFactory,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

import {
  IndividualOffersScreen,
  IndividualOffersScreenProps,
} from '../IndividualOffersScreen'

const renderOffers = (props: IndividualOffersScreenProps) => {
  const user = sharedCurrentUserFactory({ navState: null })
  renderWithProviders(<IndividualOffersScreen {...props} />, {
    user,
    storeOverrides: {
      user: {
        selectedOffererId: 1,
        currentUser: user,
      },
    },
  })
}

vi.mock('apiClient/api', () => ({
  api: {
    listOfferersNames: vi.fn(),
  },
}))

describe('tracker IndividualOffersScreen', () => {
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
      offererAddresses: [],
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
