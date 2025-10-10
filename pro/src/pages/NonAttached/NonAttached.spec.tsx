import { screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { NonAttached } from './NonAttached'

const render = () => {
  return renderWithProviders(<NonAttached />)
}

describe('NonAttached', () => {
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
