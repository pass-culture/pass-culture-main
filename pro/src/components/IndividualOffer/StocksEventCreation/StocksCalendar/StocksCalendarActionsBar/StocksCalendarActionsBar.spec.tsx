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
  it('should show the navigation links in the action bar when no stock is checked yet', () => {
    renderStocksCalendarActionsBar()

    expect(
      screen.getByRole('button', { name: 'Annuler et quitter' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: 'Enregistrer les modifications' })
    ).toBeInTheDocument()
  })

  it('should trigger the navigation to the form previous and next steps', async () => {
    const nextStepMock = vi.fn()
    const previousStepMock = vi.fn()

    renderStocksCalendarActionsBar({
      handleNextStep: nextStepMock,
      handlePreviousStep: previousStepMock,
      hasStocks: true,
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Annuler et quitter' })
    )
    expect(previousStepMock).toHaveBeenCalled()

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
