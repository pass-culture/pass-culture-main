import { screen } from '@testing-library/react'

import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { OfferTypeScreen } from './OfferType'

const renderOfferTypeScreen = ({
  isNewOfferCreationFlowFeatureActive
}: {
  isNewOfferCreationFlowFeatureActive?: boolean
} = {}) => {
  renderWithProviders(
    <OfferTypeScreen />,
    {
      features: isNewOfferCreationFlowFeatureActive ? ['WIP_ENABLE_NEW_OFFER_CREATION_FLOW']: []
    }
  )
}

describe('OfferType', () => {
  it('should display the offer subtype options', () => {
    renderOfferTypeScreen()

    expect(screen.getByTestId('wrapper-individualOfferSubtype')).toBeInTheDocument()
  })

  it('should NOT display the offer subtype options', () => {
    renderOfferTypeScreen({isNewOfferCreationFlowFeatureActive: true})

    expect(screen.queryByTestId('wrapper-individualOfferSubtype')).not.toBeInTheDocument()
  })
})
