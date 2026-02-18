import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import type { RouteObject } from 'react-router'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { DownloadDropdown } from '../DownloadDropdown'

const mockLogEvent = vi.fn()
vi.mock('@/app/App/analytics/firebase', () => ({
  useAnalytics: () => ({ logEvent: mockLogEvent }),
}))

const defaultProps = {
  logEventNames: {
    onSelectCsv: 'downloadCsv',
    onSelectXls: 'downloadXls',
    onToggle: 'downloadToggle',
  },
  onSelect: vi.fn().mockResolvedValue(undefined),
  title: 'Télécharger les offres',
}

const renderDownloadDropdown = (
  props: Partial<React.ComponentProps<typeof DownloadDropdown>> = {}
) => {
  const routes: RouteObject[] = [
    {
      path: '/test-page',
      element: <DownloadDropdown {...defaultProps} {...props} />,
    },
  ]

  renderWithProviders(null, {
    routes,
    initialRouterEntries: ['/test-page'],
  })
}

describe('DownloadDropdown', () => {
  it('should render the download button', () => {
    renderDownloadDropdown()

    expect(
      screen.getByRole('button', { name: 'Télécharger' })
    ).toBeInTheDocument()
  })

  it('should disable the button when isDisabled is true', () => {
    renderDownloadDropdown({ isDisabled: true })

    expect(screen.getByRole('button', { name: 'Télécharger' })).toBeDisabled()
  })

  it('should log toggle event when clicking the button', async () => {
    renderDownloadDropdown()

    await userEvent.click(screen.getByRole('button', { name: 'Télécharger' }))

    expect(mockLogEvent).toHaveBeenCalledWith('downloadToggle', {
      from: '/test-page',
    })
  })

  it('should display XLS and CSV options when dropdown is open', async () => {
    renderDownloadDropdown()

    await userEvent.click(screen.getByRole('button', { name: 'Télécharger' }))

    expect(
      screen.getByRole('menuitem', { name: 'Microsoft Excel (.xls)' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('menuitem', { name: 'Fichier CSV (.csv)' })
    ).toBeInTheDocument()
  })

  it('should call onSelect with XLS and log event when clicking XLS option', async () => {
    const onSelect = vi.fn().mockResolvedValue(undefined)
    renderDownloadDropdown({ onSelect })

    await userEvent.click(screen.getByRole('button', { name: 'Télécharger' }))
    await userEvent.click(
      screen.getByRole('menuitem', { name: 'Microsoft Excel (.xls)' })
    )

    expect(onSelect).toHaveBeenCalledWith('XLS')
    expect(mockLogEvent).toHaveBeenCalledWith('downloadXls', {
      from: '/test-page',
    })
  })

  it('should call onSelect with CSV and log event when clicking CSV option', async () => {
    const onSelect = vi.fn().mockResolvedValue(undefined)
    renderDownloadDropdown({ onSelect })

    await userEvent.click(screen.getByRole('button', { name: 'Télécharger' }))
    await userEvent.click(
      screen.getByRole('menuitem', { name: 'Fichier CSV (.csv)' })
    )

    expect(onSelect).toHaveBeenCalledWith('CSV')
    expect(mockLogEvent).toHaveBeenCalledWith('downloadCsv', {
      from: '/test-page',
    })
  })
})
