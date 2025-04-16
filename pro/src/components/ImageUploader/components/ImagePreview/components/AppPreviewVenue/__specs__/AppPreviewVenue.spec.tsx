import { screen } from '@testing-library/react'

import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { AppPreviewVenue, AppPreviewVenueProps } from '../AppPreviewVenue'

const renderAppPreviewVenue = (props: AppPreviewVenueProps) =>
  renderWithProviders(<AppPreviewVenue {...props} />)

describe('AppPreviewVenue', () => {
  let props: AppPreviewVenueProps

  beforeEach(() => {
    props = {
      imageUrl: '/noimage.jpg',
    }
  })

  it('should render app preview venue', () => {
    renderAppPreviewVenue(props)

    expect(screen.getByTestId('app-preview-venue-img-home')).toBeInTheDocument()
    expect(screen.getByTestId('app-preview-venue-img')).toBeInTheDocument()
  })
})
