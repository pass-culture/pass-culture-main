import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { api } from '@/apiClient/api'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { HighlightHome } from './HighlightHome'

describe('HighlightHome', () => {
  it('should render and pass accessibility checks', async () => {
    vi.spyOn(api, 'getHighlights').mockResolvedValue([])

    const { container } = renderWithProviders(<HighlightHome />)

    expect(
      await screen.findByRole('heading', {
        name: 'Valorisez vos évènements en les associant à un temps fort du pass Culture !',
      })
    ).toBeInTheDocument()

    expect(
      //  Ingore the color contrast to avoid an axe-core error cf https://github.com/NickColley/jest-axe/issues/147
      await axe(container, {
        rules: { 'color-contrast': { enabled: false } },
      })
    ).toHaveNoViolations()
  })

  it('should open the highlight modal ', async () => {
    vi.spyOn(api, 'getHighlights').mockResolvedValue([])

    renderWithProviders(<HighlightHome />)

    await userEvent.click(screen.getByText('Parcourir les temps forts'))

    expect(
      screen.getByRole('heading', {
        name: 'Qu’est-ce qu’un temps fort sur le pass Culture ?',
      })
    ).toBeInTheDocument()
  })
})
