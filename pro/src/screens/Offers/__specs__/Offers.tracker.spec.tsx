import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import * as router from 'react-router-dom'

import { api } from 'apiClient/api'
import { UserRole } from 'apiClient/v1'
import { DEFAULT_SEARCH_FILTERS } from 'core/Offers/constants'
import { Audience } from 'core/shared'
import { offererFactory } from 'utils/apiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import Offers, { OffersProps } from '../Offers'

vi.mock('react-router-dom', async () => ({
  ...((await vi.importActual('react-router-dom')) ?? {}),
  useLoaderData: vi.fn(),
}))

const renderOffers = (props: OffersProps) =>
  renderWithProviders(<Offers {...props} />)

vi.mock('apiClient/api', () => ({
  api: {
    listOfferersNames: vi.fn(),
  },
}))

describe('tracker screen Offers', () => {
  it('should track when cliking on offer link', async () => {
    // Given
    vi.spyOn(router, 'useLoaderData').mockReturnValue({ offers: [] })
    const props = {
      currentPageNumber: 1,
      isLoading: false,
      currentUser: {
        isAdmin: false,
        roles: [UserRole.PRO],
      },
      loadAndUpdateOffers: vi.fn(),
      offerer: offererFactory(),
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

    const individualOffererNames = offererFactory()
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: [individualOffererNames],
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
