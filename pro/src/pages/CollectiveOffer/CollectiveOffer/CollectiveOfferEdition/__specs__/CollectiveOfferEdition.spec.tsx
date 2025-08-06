import { screen, waitFor } from '@testing-library/react'

import { api } from '@/apiClient//api'
import * as hooks from '@/commons/hooks/swr/useOfferer'
import { getCollectiveOfferFactory } from '@/commons/utils/factories/collectiveApiFactories'
import { defaultGetOffererResponseModel } from '@/commons/utils/factories/individualApiFactories'
import {
  currentOffererFactory,
  sharedCurrentUserFactory,
} from '@/commons/utils/factories/storeFactories'
import {
  managedVenueFactory,
  userOffererFactory,
} from '@/commons/utils/factories/userOfferersFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { MandatoryCollectiveOfferFromParamsProps } from '../../components/OfferEducational/useCollectiveOfferFromParams'
import { CollectiveOfferEdition } from '../CollectiveOfferEdition'

vi.mock('@/apiClient//api', () => ({
  api: {
    listEducationalDomains: vi.fn(),
    listEducationalOfferers: vi.fn(),
    getCollectiveOffer: vi.fn(),
    getCollectiveOfferTemplate: vi.fn(),
  },
}))

const renderCollectiveOfferEdition = (
  path: string,
  props: MandatoryCollectiveOfferFromParamsProps
) => {
  renderWithProviders(<CollectiveOfferEdition {...props} />, {
    initialRouterEntries: [path],
    storeOverrides: {
      user: { currentUser: sharedCurrentUserFactory() },
      offerer: currentOffererFactory({
        currentOfferer: { id: 10 },
      }),
    },
  })
}

describe('CollectiveOfferEdition', () => {
  const venue = managedVenueFactory({ id: 1 })
  const offerer = userOffererFactory({
    id: 1,
    name: 'Ma super structure',
    managedVenues: [venue],
  })
  const defaultProps = {
    offer: getCollectiveOfferFactory({}),
    isTemplate: false,
  }

  const mockOffererData = {
    data: { ...defaultGetOffererResponseModel, isValidated: true },
    isLoading: false,
    error: undefined,
    mutate: vi.fn(),
    isValidating: false,
  }

  beforeEach(() => {
    vi.spyOn(api, 'listEducationalOfferers').mockResolvedValue({
      educationalOfferers: [offerer],
    })
    vi.spyOn(hooks, 'useOfferer').mockReturnValue(mockOffererData)
  })

  it('should render collective offer edition form', async () => {
    renderCollectiveOfferEdition('/offre/edition/collectif', {
      ...defaultProps,
    })

    expect(
      await screen.findByRole('heading', {
        name: /Éditer une offre collective/,
      })
    ).toBeInTheDocument()

    await waitFor(() => {
      expect(
        screen.getByRole('heading', {
          name: 'Quel est le type de votre offre ?',
        })
      ).toBeInTheDocument()
    })
  })

  it('should render with template tag', async () => {
    renderCollectiveOfferEdition('/offre/edition/collectif/vitrine', {
      ...defaultProps,
      isTemplate: true,
    })
    expect(
      await screen.findByRole('heading', {
        name: /Éditer une offre collective/,
      })
    ).toBeInTheDocument()
    expect(screen.getByText('Offre vitrine')).toBeInTheDocument()
  })
})
