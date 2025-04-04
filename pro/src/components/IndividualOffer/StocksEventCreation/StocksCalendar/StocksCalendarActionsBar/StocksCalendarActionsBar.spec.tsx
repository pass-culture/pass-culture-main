import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { renderWithProviders } from 'commons/utils/renderWithProviders'
import { Notification } from 'components/Notification/Notification'

import {
  StocksCalendarActionsBar,
  StocksCalendarActionsBarProps,
} from './StocksCalendarActionsBar'

function renderStocksCalendarActionsBar(
  props?: Partial<StocksCalendarActionsBarProps>
) {
  return renderWithProviders(
    <>
      <StocksCalendarActionsBar
        checkedStocks={new Set([])}
        deleteStocks={() => {}}
        handleNextStep={() => {}}
        handlePreviousStep={() => {}}
        hasStocks={false}
        updateCheckedStocks={() => {}}
        {...props}
      />
      <Notification />
    </>
  )
}

describe('StocksCalendarActionsBar', () => {
  it('should show the navigation options when no stock is checked', () => {
    renderStocksCalendarActionsBar()

    expect(screen.getByRole('button', { name: 'Annuler et quitter' }))
    expect(
      screen.getByRole('button', { name: 'Enregistrer les modifications' })
    ).toBeInTheDocument()
  })

  it('should trigger the navigation to the form previous and next steps', async () => {
    const nextStepMock = vi.fn()
    const previousStepStepMock = vi.fn()

    renderStocksCalendarActionsBar({
      handleNextStep: nextStepMock,
      handlePreviousStep: previousStepStepMock,
      hasStocks: true,
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Annuler et quitter' })
    )
    expect(previousStepStepMock).toHaveBeenCalled()

    await userEvent.click(
      screen.getByRole('button', { name: 'Enregistrer les modifications' })
    )
    expect(nextStepMock).toHaveBeenCalled()
  })

  it('should show an error message when going to the next step without having added any stock', async () => {
    renderStocksCalendarActionsBar()

    await userEvent.click(
      screen.getByRole('button', { name: 'Enregistrer les modifications' })
    )

    expect(
      screen.getByText('Veuillez renseigner au moins une date')
    ).toBeInTheDocument()
  })

  it('should show the checked stocks action bar when some stocks are checked', () => {
    renderStocksCalendarActionsBar({
      hasStocks: true,
      checkedStocks: new Set([1]),
    })

    expect(
      screen.queryByRole('button', { name: 'Enregistrer les modifications' })
    ).not.toBeInTheDocument()

    expect(
      screen.getByRole('button', { name: 'Désélectionner' })
    ).toBeInTheDocument()

    expect(
      screen.getByRole('button', { name: 'Supprimer cette date' })
    ).toBeInTheDocument()
  })

  it('should trigger the deletion of all checked stocks', async () => {
    const deleteStocks = vi.fn()

    renderStocksCalendarActionsBar({
      hasStocks: true,
      checkedStocks: new Set([1, 2]),
      deleteStocks: deleteStocks,
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Supprimer ces dates' })
    )

    expect(deleteStocks).toHaveBeenCalled()
  })

  it('should uncheck all checked stocks', async () => {
    const updateCheckedStocks = vi.fn()

    renderStocksCalendarActionsBar({
      hasStocks: true,
      checkedStocks: new Set([1, 2]),
      updateCheckedStocks: updateCheckedStocks,
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Désélectionner' })
    )

    expect(updateCheckedStocks).toHaveBeenCalled()
  })
})
