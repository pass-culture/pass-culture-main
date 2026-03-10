import { screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { NonAttachedBanner } from './NonAttachedBanner'

const render = () => {
  return renderWithProviders(<NonAttachedBanner />)
}

describe('NonAttachedBanner', () => {
  it('should render without errors', async () => {
    const { container } = render()
    expect(
      screen.getByText(
        /Votre rattachement est en cours de traitement par les équipes du pass Culture/
      )
    ).toBeInTheDocument()
    expect(screen.getByText(/En savoir plus/)).toBeInTheDocument()

    expect(await axe(container)).toHaveNoViolations()
  })
})
