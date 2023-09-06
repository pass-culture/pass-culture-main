import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
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

vi.mock('react-router-dom', async () => ({
  ...((await vi.importActual('react-router-dom')) ?? {}),
  useNavigate: vi.fn(),
}))

const renderOfferTypes = async (venueId?: string) => {
  const storeOverrides = {
    user: {
      initialized: true,
      currentUser: {
        isAdmin: false,
        email: 'email@example.com',
      },
    },
    features: {
      list: [{ isActive: true, nameKey: 'WIP_CATEGORY_SELECTION' }],
    },
  }

  renderWithProviders(<OfferType />, {
    storeOverrides,
    initialRouterEntries: [`/creation${venueId ? `?lieu=${venueId}` : ''}`],
  })
}

describe('screens:OfferIndividual::OfferType', () => {
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

    await userEvent.click(screen.getByText('Un bien physique'))
    await userEvent.click(screen.getByText('Étape suivante'))

    expect(mockNavigate).toHaveBeenCalledWith({
      pathname: '/offre/individuelle/creation/informations',
      search: '?offer-type=PHYSICAL_GOOD',
    })
  })

  it('should redirect with offer type when venue and type selected', async () => {
    renderOfferTypes('123')

    expect(
      await screen.findByText('Quel est la catégorie de l’offre ?')
    ).toBeInTheDocument()
    await userEvent.click(screen.getByText('autre'))
    await userEvent.click(screen.getByText('Un évènement physique daté'))
    await userEvent.click(screen.getByText('Étape suivante'))

    expect(mockNavigate).toHaveBeenCalledWith({
      pathname: '/offre/individuelle/creation/informations',
      search: '?lieu=123&offer-type=PHYSICAL_EVENT',
    })
  })

  it('should redirect with subcategory when venue and subcategory selected', async () => {
    renderOfferTypes('123')

    expect(
      await screen.findByText('Quel est la catégorie de l’offre ?')
    ).toBeInTheDocument()
    await userEvent.click(screen.getByText('Ma sous-catégorie préférée'))
    await userEvent.click(screen.getByText('Étape suivante'))

    expect(mockNavigate).toHaveBeenCalledWith({
      pathname: '/offre/individuelle/creation/informations',
      search: '?lieu=123&sous-categorie=SPECTACLE_REPRESENTATION',
    })
  })
})
