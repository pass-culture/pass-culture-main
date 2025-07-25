import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'

import { TableNoFilterResult } from './TableNoFilterResult'

describe('<TableNoFilterResult />', () => {
  it('renders the default message and elements', () => {
    const resetFilters = vi.fn()

    render(
      <table>
        <tbody>
          <TableNoFilterResult
            colSpan={3}
            resetFilters={resetFilters}
            message="Aucun résultat trouvé"
          />
        </tbody>
      </table>
    )

    expect(screen.getByText('Aucun résultat trouvé')).toBeInTheDocument()
    expect(
      screen.getByText('Vous pouvez modifier votre recherche ou')
    ).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: /Réinitialiser les filtres/i })
    ).toBeInTheDocument()
    expect(
      screen.getByLabelText(/Illustration de recherche/i)
    ).toBeInTheDocument()
  })

  it('calls resetFilters when button is clicked', async () => {
    const resetFilters = vi.fn()
    const user = userEvent.setup()

    render(
      <table>
        <tbody>
          <TableNoFilterResult
            colSpan={3}
            resetFilters={resetFilters}
            message="Aucun résultat trouvé"
          />
        </tbody>
      </table>
    )

    const button = screen.getByRole('button', {
      name: /Réinitialiser les filtres/i,
    })
    await user.click(button)

    expect(resetFilters).toHaveBeenCalledTimes(1)
  })
})
