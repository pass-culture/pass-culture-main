import { screen } from '@testing-library/react'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { OfferTypeScreen, type OfferTypeScreenProps } from './OfferType'

const defaultProps: OfferTypeScreenProps = { collectiveOnly: false }

const renderOfferTypeScreen = (
  props: Partial<OfferTypeScreenProps>,
  features: string[]
) => {
  renderWithProviders(<OfferTypeScreen {...defaultProps} {...props} />, {
    features: features,
  })
}

describe('OfferType', () => {
  it('should show the individual option if the FF WIP_ENABLE_NEW_OFFER_CREATION_FLOW is enabled and the form is not collective only', () => {
    renderOfferTypeScreen({}, ['WIP_ENABLE_NEW_OFFER_CREATION_FLOW'])

    expect(
      screen.getByRole('heading', { name: 'À qui destinez-vous cette offre ?' })
    ).toBeInTheDocument()
  })

  it('should not show the individual option if the FF WIP_ENABLE_NEW_OFFER_CREATION_FLOW is enabled and the query params contain the type "collective"', () => {
    renderOfferTypeScreen({ collectiveOnly: true }, [
      'WIP_ENABLE_NEW_OFFER_CREATION_FLOW',
    ])

    expect(
      screen.queryByRole('heading', {
        name: 'À qui destinez-vous cette offre ?',
      })
    ).not.toBeInTheDocument()
  })

  it('should not show the individual categories options if the FF WIP_ENABLE_NEW_OFFER_CREATION_FLOW is enabled', () => {
    renderOfferTypeScreen({}, ['WIP_ENABLE_NEW_OFFER_CREATION_FLOW'])

    expect(
      screen.queryByRole('heading', {
        name: 'Votre offre est',
      })
    ).not.toBeInTheDocument()
  })
})
