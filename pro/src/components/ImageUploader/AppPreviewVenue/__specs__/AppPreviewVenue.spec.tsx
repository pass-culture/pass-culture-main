import { screen } from '@testing-library/react'
import React from 'react'

import { renderWithProviders } from 'utils/renderWithProviders'

import AppPreviewVenue, { AppPreviewVenueProps } from '../AppPreviewVenue'

const renderAppPreviewVenue = (props: AppPreviewVenueProps) =>
  renderWithProviders(<AppPreviewVenue {...props} />)

describe('AppPreviewVenue', () => {
  let props: AppPreviewVenueProps

  beforeEach(() => {
    props = {
      imageUrl: '/noimage.jpg',
    }
  })

  it('should render app preview venue', async () => {
    await renderAppPreviewVenue(props)
    expect(screen.getByTestId('app-preview-venue-img-home')).toBeInTheDocument()
    expect(screen.getByTestId('app-preview-venue-img')).toBeInTheDocument()
  })
})
