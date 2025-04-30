import { render, screen } from '@testing-library/react'
import { expect } from 'vitest'

import { AppPreviewVenue } from './AppPreviewVenue'

describe('AppPreviewVenue', () => {
  const testImageUrl = 'https://example.com/test-image.jpg'

  it('renders home preview image', () => {
    render(<AppPreviewVenue imageUrl={testImageUrl} />)
    const homeImage = screen.getByTestId('app-preview-offer-img-home')
    expect(homeImage).toBeInTheDocument()
    expect(homeImage).toHaveAttribute('src', testImageUrl)
  })

  it('renders offer preview image', () => {
    render(<AppPreviewVenue imageUrl={testImageUrl} />)
    const venueImage = screen.getByTestId('app-preview-offer-img')
    expect(venueImage).toBeInTheDocument()
    expect(venueImage).toHaveAttribute('src', testImageUrl)
  })
})
