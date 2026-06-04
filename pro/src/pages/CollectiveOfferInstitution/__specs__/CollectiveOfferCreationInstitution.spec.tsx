import { screen } from '@testing-library/react'

import { getCollectiveOfferFactory } from '@/commons/utils/factories/collectiveApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import type { MandatoryCollectiveOfferFromParamsProps } from '@/pages/CollectiveOffer/CollectiveOffer/components/OfferEducational/useCollectiveOfferFromParams'

import { CollectiveOfferCreationInstitution } from '../CollectiveOfferCreationInstitution'

const renderCollectiveOfferCreationInstitution = (
  path: string,
  props: MandatoryCollectiveOfferFromParamsProps,
  storeOverride?: any
) => {
  renderWithProviders(<CollectiveOfferCreationInstitution {...props} />, {
    initialRouterEntries: [path],
    storeOverrides: {
      user: {
        currentUser: sharedCurrentUserFactory(),
        selectedPartnerVenue: makeGetVenueResponseModel({
          id: 1,
          allowedOnAdage: true,
        }),
      },
      ...storeOverride,
    },
  })
}

const defaultProps = {
  offer: getCollectiveOfferFactory(),
  isTemplate: false,
  offerer: undefined,
}

describe('CollectiveOfferCreationInstitution', () => {
  it('should render collective offer institution form', async () => {
    renderCollectiveOfferCreationInstitution(
      '/offre/A1/collectif/etablissement',
      defaultProps
    )

    expect(
      await screen.findByRole('heading', {
        name: /Créer une offre/,
      })
    ).toBeInTheDocument()

    expect(
      screen.getByRole('heading', {
        name: "Renseignez l'établissement scolaire et l'enseignant",
      })
    ).toBeInTheDocument()
  })
})
