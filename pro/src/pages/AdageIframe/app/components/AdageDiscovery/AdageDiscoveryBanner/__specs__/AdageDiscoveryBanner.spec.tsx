import { render, screen } from '@testing-library/react'

import { AdageDiscoveryBanner } from '../AdageDiscoveryBanner'

Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: () => ({
    matches: true,
  }),
})

describe('AdageDiscoveryBanner', () => {
  it('should display the title of the adage discovery page', () => {
    render(<AdageDiscoveryBanner />)

    expect(
      screen.getByRole('heading', {
        name: 'Découvrez la part collective du pass Culture',
      })
    ).toBeInTheDocument()
  })

  it('should not reposition svg groups when the user scrolls when the user prefers reduced motion', () => {
    Object.defineProperty(window, 'scrollY', { value: 100 })

    render(<AdageDiscoveryBanner />)

    document.dispatchEvent(new CustomEvent('scroll', { detail: 100 }))

    expect(screen.getByTestId('banner-ovals-group').style.transform).toBeFalsy()
  })
})
