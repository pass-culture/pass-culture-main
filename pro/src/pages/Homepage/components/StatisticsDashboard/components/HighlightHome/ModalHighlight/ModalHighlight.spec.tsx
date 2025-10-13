import { screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { api } from '@/apiClient/api'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { ModalHighlight } from './ModalHighlight'

describe('ModalHighlight', () => {
  it('should render and pass accessibility checks', async () => {
    vi.spyOn(api, 'getHighlights').mockResolvedValue([
      {
        name: 'my name',
        description: 'my description',
        availabilityTimespan: [new Date(), new Date()],
        id: 1,
        mediationUrl: 'url.example',
        highlightTimespan: [new Date(), new Date()],
      },
    ])

    const { container } = renderWithProviders(<ModalHighlight open />)

    expect(
      await screen.findByRole('heading', {
        name: 'Qu’est-ce qu’un temps fort sur le pass Culture ?',
      })
    ).toBeInTheDocument()

    expect(
      await screen.findByRole('heading', {
        name: 'my name',
      })
    ).toBeInTheDocument()

    expect(
      //  Ingore the color contrast to avoid an axe-core error cf https://github.com/NickColley/jest-axe/issues/147
      await axe(container, {
        rules: { 'color-contrast': { enabled: false } },
      })
    ).toHaveNoViolations()
  })
})
