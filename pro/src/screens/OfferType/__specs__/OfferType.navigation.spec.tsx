import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import * as router from 'react-router-dom'

import { api } from 'apiClient/api'
import { SubcategoryIdEnum, VenueTypeCode } from 'apiClient/v1'
import {
  individualOfferCategoryFactory,
  individualOfferSubCategoryResponseModelFactory,
  individualOfferVenueResponseModelFactory,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import OfferType from '../OfferType'

vi.mock('hooks/useRemoteConfig', () => ({
  __esModule: true,
  default: () => ({
    remoteConfig: {},
  }),
}))

vi.mock('@firebase/remote-config', () => ({
  getValue: () => ({ asBoolean: () => true }),
}))

vi.mock('react-router-dom', async () => ({
  ...((await vi.importActual('react-router-dom')) ?? {}),
  useNavigate: vi.fn(),
}))

const renderOfferTypes = (venueId?: string) => {
  const storeOverrides = {
    user: {
      initialized: true,
      currentUser: {
        isAdmin: false,
        email: 'email@example.com',
      },
    },
  }

  renderWithProviders(<OfferType />, {
    storeOverrides,
    initialRouterEntries: [`/creation${venueId ? `?lieu=${venueId}` : ''}`],
  })
}

describe('screens:IndividualOffer::OfferType', () => {
  const mockNavigate = vi.fn()

  beforeEach(() => {
    vi.spyOn(api, 'getCategories').mockResolvedValue({
      categories: [individualOfferCategoryFactory()],
      subcategories: [
        individualOfferSubCategoryResponseModelFactory({
          // id should match venueType in venueTypeSubcategoriesMapping
          id: SubcategoryIdEnum.SPECTACLE_REPRESENTATION,
          proLabel: 'Ma sous-catégorie préférée',
        }),
      ],
    })
    vi.spyOn(api, 'getVenue').mockResolvedValue({
      ...individualOfferVenueResponseModelFactory({
        venueTypeCode: 'OTHER' as VenueTypeCode, // cast is needed because VenueTypeCode in apiClient is defined in french, but sent by api in english
      }),
    })

    vi.spyOn(router, 'useNavigate').mockReturnValue(mockNavigate)
  })

  it('should redirect with offer type when no venue and type selected', async () => {
    renderOfferTypes()

    await userEvent.click(await screen.findByText('Un bien physique'))
    await userEvent.click(screen.getByText('Étape suivante'))

    expect(mockNavigate).toHaveBeenCalledWith({
      pathname: '/offre/individuelle/creation/informations',
      search: 'offer-type=PHYSICAL_GOOD',
    })
  })

  it('should redirect with the offer type when venue and type selected', async () => {
    renderOfferTypes('123')

    await userEvent.click(screen.getByText('Un évènement physique daté'))
    await userEvent.click(screen.getByText('Étape suivante'))

    expect(mockNavigate).toHaveBeenCalledWith({
      pathname: '/offre/individuelle/creation/informations',
      search: 'lieu=123&offer-type=PHYSICAL_EVENT',
    })
  })

  it('should diable button when type was not selected', async () => {
    renderOfferTypes('123')

    // type is not selected
    expect(screen.getByText('Étape suivante')).toBeDisabled()

    await userEvent.click(screen.getByText('Un évènement physique daté'))
    expect(screen.getByText('Étape suivante')).not.toBeDisabled()
  })
})
