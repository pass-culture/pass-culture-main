import { screen } from '@testing-library/react'

import { api } from 'apiClient/api'
import { getCollectiveOfferFactory } from 'commons/utils/factories/collectiveApiFactories'
import {
  managedVenueFactory,
  userOffererFactory,
} from 'commons/utils/factories/userOfferersFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'
import { OptionalCollectiveOfferFromParamsProps } from 'pages/CollectiveOffer/CollectiveOffer/components/OfferEducational/useCollectiveOfferFromParams'

import { CollectiveOfferCreation } from '../CollectiveOfferCreation'

vi.mock('apiClient/api', () => ({
  api: {
    getCategories: vi.fn(),
    listEducationalDomains: vi.fn(),
    listEducationalOfferers: vi.fn(),
    getCollectiveOffer: vi.fn(),
    getCollectiveOfferTemplate: vi.fn(),
    getNationalPrograms: vi.fn(),
  },
}))

const renderCollectiveOfferCreation = (
  path: string,
  props: OptionalCollectiveOfferFromParamsProps
) => {
  renderWithProviders(<CollectiveOfferCreation {...props} />, {
    initialRouterEntries: [path],
  })
}

describe('CollectiveOfferCreation', () => {
  const venue = managedVenueFactory({ id: 1 })
  const offerer = userOffererFactory({
    id: 1,
    name: 'Ma super structure',
    managedVenues: [venue],
  })
  const defaultProps = {
    offer: getCollectiveOfferFactory({
      venue: { ...venue, managingOfferer: offerer },
    }),
    isTemplate: false,
  }
  beforeEach(() => {
    vi.spyOn(api, 'listEducationalOfferers').mockResolvedValue({
      educationalOfferers: [offerer],
    })
    vi.spyOn(api, 'getCategories').mockResolvedValue({
      categories: [],
      subcategories: [],
    })
    vi.spyOn(api, 'listEducationalDomains').mockResolvedValue([])
    vi.spyOn(api, 'getNationalPrograms').mockResolvedValue([])
  })
  it('should render collective offer creation form', async () => {
    renderCollectiveOfferCreation('/offre/creation/collectif', {
      ...defaultProps,
    })
    expect(
      await screen.findByRole('heading', {
        name: /Créer une offre/,
      })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('heading', {
        name: 'Qui propose l’offre ?',
      })
    ).toBeInTheDocument()
  })

  it('should render with template tag', async () => {
    renderCollectiveOfferCreation('/offre/creation/collectif/vitrine', {
      ...defaultProps,
      isTemplate: true,
    })
    expect(
      await screen.findByRole('heading', {
        name: /Créer une offre/,
      })
    ).toBeInTheDocument()
    expect(screen.getByText('Offre vitrine')).toBeInTheDocument()
  })
})
