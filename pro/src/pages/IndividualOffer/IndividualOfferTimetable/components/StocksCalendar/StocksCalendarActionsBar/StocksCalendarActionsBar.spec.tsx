import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { SnackBarContainer } from '@/components/SnackBarContainer/SnackBarContainer'

import {
  StocksCalendarActionsBar,
  type StocksCalendarActionsBarProps,
} from './StocksCalendarActionsBar'

const mockNavigate = vi.fn()

vi.mock('react-router', async () => {
  const actual = await vi.importActual('react-router')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

function renderStocksCalendarActionsBar(
  props?: Partial<StocksCalendarActionsBarProps>
) {
  return renderWithProviders(
    <>
      <StocksCalendarActionsBar
        mode={OFFER_WIZARD_MODE.CREATION}
        offerId={1}
        checkedStocks={new Set([])}
        deleteStocks={() => {}}
        hasStocks={false}
        updateCheckedStocks={() => {}}
        {...props}
      />
      <SnackBarContainer />
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

  it('should trigger the navigation to the form previous and next steps when editing the offer', async () => {
    renderStocksCalendarActionsBar({
      hasStocks: true,
      mode: OFFER_WIZARD_MODE.EDITION,
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Annuler et quitter' })
    )
    expect(mockNavigate).toHaveBeenLastCalledWith(
      '/offre/individuelle/1/horaires'
    )

    await userEvent.click(
      screen.getByRole('button', { name: 'Enregistrer les modifications' })
    )
    expect(mockNavigate).toHaveBeenLastCalledWith(
      '/offre/individuelle/1/edition/informations_pratiques'
    )
  })

  it('should trigger the navigation to the form previous and next steps when creating the offer', async () => {
    renderStocksCalendarActionsBar({
      hasStocks: true,
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Annuler et quitter' })
    )
    expect(mockNavigate).toHaveBeenLastCalledWith(
      '/offre/individuelle/1/creation/tarifs'
    )

    await userEvent.click(
      screen.getByRole('button', { name: 'Enregistrer les modifications' })
    )
    expect(mockNavigate).toHaveBeenLastCalledWith(
      '/offre/individuelle/1/creation/informations_pratiques'
    )
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

  it('should show an error message if there is no stocks when clicking on the next step', async () => {
    renderStocksCalendarActionsBar({
      hasStocks: false,
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Enregistrer les modifications' })
    )

    expect(
      screen.getByText('Veuillez renseigner au moins une date')
    ).toBeInTheDocument()
  })

  it('should show an error message in handleNextStep when hasStocks is false', async () => {
    renderStocksCalendarActionsBar({
      hasStocks: false,
    })

    // Cliquer sur le bouton pour appeler handleNextStep avec hasStocks: false
    await userEvent.click(
      screen.getByRole('button', { name: 'Enregistrer les modifications' })
    )

    // Vérifier que handleNextStep a été appelé et a affiché le message d'erreur (lignes 68-71)
    expect(
      screen.getByText('Veuillez renseigner au moins une date')
    ).toBeInTheDocument()
    // Vérifier que la navigation n'a pas été déclenchée
    expect(mockNavigate).not.toHaveBeenCalled()
  })
})
