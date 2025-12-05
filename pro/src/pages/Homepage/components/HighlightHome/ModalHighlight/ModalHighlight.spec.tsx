import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { api } from '@/apiClient/api'
import * as useAnalytics from '@/app/App/analytics/firebase'
import { HighlightEvents } from '@/commons/core/FirebaseEvents/constants'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { ModalHighlight } from './ModalHighlight'

const mockLogEvent = vi.fn()

describe('ModalHighlight', () => {
  it('should render and pass accessibility checks', async () => {
    vi.spyOn(api, 'getHighlights').mockResolvedValue([
      {
        name: 'my name',
        description: 'my description',
        availabilityDatespan: ['2025-01-01', '2025-01-15'],
        id: 1,
        mediationUrl: 'url.example',
        highlightDatespan: ['2025-02-01', '2025-02-15'],
        communicationDate: '2025-02-01',
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

    expect(screen.getByText('01/02/2025')).toBeInTheDocument()
    expect(screen.getByText('15/02/2025')).toBeInTheDocument()
    // communicationDate minus 5 days
    expect(screen.getByText('27/01/2025')).toBeInTheDocument()

    expect(
      //  Ingore the color contrast to avoid an axe-core error cf https://github.com/NickColley/jest-axe/issues/147
      await axe(container, {
        rules: { 'color-contrast': { enabled: false } },
      })
    ).toHaveNoViolations()
  })

  it('should log info to data', async () => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
    vi.spyOn(api, 'getHighlights').mockResolvedValue([
      {
        name: 'my name',
        description: 'my description',
        availabilityDatespan: ['2025-01-01', '2025-01-15'],
        id: 1,
        mediationUrl: 'url.example',
        highlightDatespan: ['2025-01-01', '2025-01-15'],
        communicationDate: '2025-01-01',
      },
    ])

    renderWithProviders(<ModalHighlight open />)

    await userEvent.click(
      screen.getByText('En savoir plus sur les temps forts')
    )

    expect(mockLogEvent).toBeCalledWith(
      HighlightEvents.HAS_CLICKED_MORE_INFO_HIGHLIGHT
    )

    await userEvent.click(screen.getByText('Voir tout le calendrier'))

    expect(mockLogEvent).toBeCalledWith(
      HighlightEvents.HAS_CLICKED_CALENDAR_HIGHLIGHT
    )

    await userEvent.click(screen.getByText('Accéder à mes offres'))

    expect(mockLogEvent).toBeCalledWith(
      HighlightEvents.HAS_CLICKED_ALL_OFFER_HIGHLIGHT
    )
  })
})
