import { screen } from '@testing-library/react'
import React from 'react'

import { renderWithProviders } from 'utils/renderWithProviders'

import CollectiveDmsTimeline from '..'

const renderCollectiveDmsTimeline = () => {
  renderWithProviders(<CollectiveDmsTimeline />)
}

describe('CollectiveDmsTimeline', () => {
  it('should render draft state', () => {
    renderCollectiveDmsTimeline()

    expect(
      screen.getByText('Déposez votre demande de référencement')
    ).toBeInTheDocument()
  })
})
