import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { addDays } from 'date-fns'

import { StocksCalendarFilters } from './StocksCalendarFilters'

describe('StocksCalendarFilters', () => {
  it('should update the sort type', async () => {
    const updateSortMock = vi.fn()

    render(
      <StocksCalendarFilters
        filters={{}}
        onUpdateFilters={vi.fn()}
        onUpdateSort={updateSortMock}
        sortType={{}}
      />
    )

    await userEvent.selectOptions(
      screen.getByLabelText('Trier par'),
      'Date décroissante'
    )

    expect(updateSortMock).toHaveBeenLastCalledWith('DATE', true)

    await userEvent.selectOptions(
      screen.getByLabelText('Trier par'),
      'Aucun tri'
    )

    expect(updateSortMock).toHaveBeenLastCalledWith('', false)
  })

  it('should update filters values', async () => {
    const updateFiltersMock = vi.fn()

    render(
      <StocksCalendarFilters
        filters={{}}
        onUpdateFilters={updateFiltersMock}
        onUpdateSort={vi.fn()}
        sortType={{}}
        priceCategories={[{ id: 1, label: 'Tarif 1', price: 1 }]}
      />
    )

    const typedDate = addDays(new Date(), 1).toISOString().split('T')[0]

    await userEvent.type(screen.getByLabelText('Date'), typedDate)

    expect(updateFiltersMock).toHaveBeenLastCalledWith(
      expect.objectContaining({
        date: typedDate,
      })
    )

    await userEvent.type(screen.getByLabelText('Horaire'), '00:00')

    expect(updateFiltersMock).toHaveBeenLastCalledWith(
      expect.objectContaining({
        time: '00:00',
      })
    )

    await userEvent.selectOptions(screen.getByLabelText('Tarif'), '1')

    expect(updateFiltersMock).toHaveBeenLastCalledWith(
      expect.objectContaining({
        priceCategoryId: '1',
      })
    )
  })

  it('should reset filters', async () => {
    const updateFiltersMock = vi.fn()

    render(
      <StocksCalendarFilters
        filters={{ time: '00:00' }}
        onUpdateFilters={updateFiltersMock}
        onUpdateSort={vi.fn()}
        sortType={{}}
      />
    )

    await userEvent.click(
      screen.getByRole('button', { name: 'Réinitialiser les filtres' })
    )

    expect(updateFiltersMock).toHaveBeenLastCalledWith({})
  })
})
