import { screen } from '@testing-library/react'

import { getCollectiveOfferFactory } from '@/commons/utils/factories/collectiveApiFactories'
import {
  currentOffererFactory,
  sharedCurrentUserFactory,
} from '@/commons/utils/factories/storeFactories'
import {
  managedVenueFactory,
  userOffererFactory,
} from '@/commons/utils/factories/userOfferersFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { MandatoryCollectiveOfferFromParamsProps } from '@/pages/CollectiveOffer/CollectiveOffer/components/OfferEducational/useCollectiveOfferFromParams'

import { CollectiveOfferStockEdition } from '../CollectiveOfferStockEdition'

vi.mock('@/apiClient/api', () => ({
  api: {},
}))

const renderCollectiveStockEdition = (
  path: string,
  props: MandatoryCollectiveOfferFromParamsProps
) => {
  renderWithProviders(<CollectiveOfferStockEdition {...props} />, {
    initialRouterEntries: [path],
    storeOverrides: {
      user: { currentUser: sharedCurrentUserFactory() },
      offerer: currentOffererFactory({
        currentOfferer: { id: 10 },
      }),
    },
  })
}

describe('CollectiveOfferStockEdition', () => {
  const venue = managedVenueFactory({ id: 1 })
  const offerer = userOffererFactory({
    id: 1,
    name: 'Ma super structure',
    managedVenues: [venue],
  })
  const defaultProps = {
    offer: getCollectiveOfferFactory({
      venue: { ...venue, managingOfferer: { ...offerer, siren: '123456789' } },
    }),
    isTemplate: false,
  }
  it('should render collective offer stock edition form', async () => {
    renderCollectiveStockEdition('/offre/A1/collectif/stocks/edition', {
      ...defaultProps,
    })

    expect(
      await screen.findByRole('heading', {
        name: /Modifier l’offre/,
      })
    ).toBeInTheDocument()
  })
})
