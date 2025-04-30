import { render, screen } from '@testing-library/react'

import { AppPreviewOffer } from './AppPreviewOffer'

describe('AppPreviewOffer', () => {
  const testImageUrl = 'https://example.com/test-image.jpg'

  it('renders home preview image', () => {
    render(<AppPreviewOffer imageUrl={testImageUrl} />)
    const homeImage = screen.getByTestId('app-preview-offer-img-home')
    expect(homeImage).toBeInTheDocument()
    expect(homeImage).toHaveAttribute('src', testImageUrl)
  })

  it('renders offer preview image', () => {
    render(<AppPreviewOffer imageUrl={testImageUrl} />)
    const offerImage = screen.getByTestId('app-preview-offer-img')
    expect(offerImage).toBeInTheDocument()
    expect(offerImage).toHaveAttribute('src', testImageUrl)
  })
})
