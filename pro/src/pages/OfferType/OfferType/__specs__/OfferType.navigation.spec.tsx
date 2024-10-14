import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import * as router from 'react-router-dom'

import { api } from 'apiClient/api'
import { SubcategoryIdEnum, VenueTypeCode } from 'apiClient/v1'
import * as useAnalytics from 'app/App/analytics/firebase'
import { defaultGetVenue } from 'commons/utils/collectiveApiFactories'
import {
  categoryFactory,
  subcategoryFactory,
} from 'commons/utils/individualApiFactories'
import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'commons/utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'commons/utils/storeFactories'

import { OfferTypeScreen } from '../OfferType'

vi.mock('@firebase/remote-config', () => ({
  getValue: () => ({ asBoolean: () => true }),
}))

vi.mock('react-router-dom', async () => ({
  ...(await vi.importActual('react-router-dom')),
  useNavigate: vi.fn(),
}))

const renderOfferTypes = (
  venueId?: string,
  options: RenderWithProvidersOptions = {}
) => {
  renderWithProviders(<OfferTypeScreen />, {
    user: sharedCurrentUserFactory(),
    initialRouterEntries: [`/creation${venueId ? `?lieu=${venueId}` : ''}`],
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
      venueTypeCode: 'OTHER' as VenueTypeCode, // cast is needed because VenueTypeCode in apiClient is defined in french, but sent by api in english
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

  it('should not display options when suggested subcategories are enabled and redirect to offer creation', async () => {
    vi.spyOn(useAnalytics, 'useRemoteConfigParams').mockReturnValue({
      SUGGESTED_CATEGORIES: 'true',
    })
    renderOfferTypes('123', {
      features: ['WIP_SUGGESTED_SUBCATEGORIES'],
    })

    expect(
      screen.queryByText('Un évènement physique daté')
    ).not.toBeInTheDocument()
    await userEvent.click(screen.getByText('Étape suivante'))

    expect(mockNavigate).toHaveBeenCalledWith({
      pathname: '/offre/individuelle/creation/informations',
      search: 'lieu=123',
    })
  })
})
