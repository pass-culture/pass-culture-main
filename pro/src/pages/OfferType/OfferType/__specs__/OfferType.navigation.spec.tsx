import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import * as router from 'react-router'

import { api } from '@/apiClient/api'
import { SubcategoryIdEnum } from '@/apiClient/v1'
import { defaultGetVenue } from '@/commons/utils/factories/collectiveApiFactories'
import {
  categoryFactory,
  defaultGetOffererResponseModel,
  makeVenueListItem,
  subcategoryFactory,
} from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { OfferTypeScreen } from '../OfferType'

vi.mock('@firebase/remote-config', () => ({
  getValue: () => ({ asBoolean: () => true }),
}))

vi.mock('react-router', async () => ({
  ...(await vi.importActual('react-router')),
  useNavigate: vi.fn(),
}))

const renderOfferTypes = (
  venueId?: string,
  options: RenderWithProvidersOptions = {}
) => {
  renderWithProviders(<OfferTypeScreen collectiveOnly={false} />, {
    user: sharedCurrentUserFactory(),
    initialRouterEntries: [`/creation${venueId ? `?lieu=${venueId}` : ''}`],
    storeOverrides: {
      user: {
        selectedVenue: makeVenueListItem({ id: 2 }),
      },
      offerer: {
        currentOfferer: { ...defaultGetOffererResponseModel, id: 1 },
      },
    },
    ...options,
  })
}

describe('screens:IndividualOffer::OfferType', () => {
  const mockNavigate = vi.fn()

  beforeEach(() => {
    vi.spyOn(api, 'getCategories').mockResolvedValue({
      categories: [categoryFactory()],
      subcategories: [
        subcategoryFactory({
          // id should match venueType in venueTypeSubcategoriesMapping
          id: SubcategoryIdEnum.SPECTACLE_REPRESENTATION,
          proLabel: 'Ma sous-catégorie préférée',
        }),
      ],
    })
    vi.spyOn(api, 'getVenue').mockResolvedValue({
      ...defaultGetVenue,
      venueType: { value: 'OTHER', label: '' },
    })

    vi.spyOn(router, 'useNavigate').mockReturnValue(mockNavigate)
  })

  it('should redirect with offer type when no venue and type selected', async () => {
    renderOfferTypes()

    await userEvent.click(await screen.findByText('Un bien physique'))
    await userEvent.click(screen.getByText('Étape suivante'))

    expect(mockNavigate).toHaveBeenCalledWith({
      pathname: '/offre/individuelle/creation/details',
      search: 'offer-type=PHYSICAL_GOOD',
    })
  })

  it('should redirect with the offer type when venue and type selected', async () => {
    renderOfferTypes('123')

    await userEvent.click(screen.getByText('Un évènement physique daté'))
    await userEvent.click(screen.getByText('Étape suivante'))

    expect(mockNavigate).toHaveBeenCalledWith({
      pathname: '/offre/individuelle/creation/details',
      search: 'lieu=123&offer-type=PHYSICAL_EVENT',
    })
  })
})
