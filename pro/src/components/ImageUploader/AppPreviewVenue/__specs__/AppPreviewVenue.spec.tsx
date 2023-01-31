import { screen } from '@testing-library/react'
import React from 'react'

import { renderWithProviders } from 'utils/renderWithProviders'

import AppPreviewVenue, { IAppPreviewVenueProps } from '../AppPreviewVenue'

const renderAppPreviewVenue = (props: IAppPreviewVenueProps) =>
  renderWithProviders(<AppPreviewVenue {...props} />)

describe('AppPreviewVenue', () => {
  let props: IAppPreviewVenueProps

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
