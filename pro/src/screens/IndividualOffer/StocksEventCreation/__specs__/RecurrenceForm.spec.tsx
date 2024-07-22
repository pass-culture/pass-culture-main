import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { addDays, format } from 'date-fns'
import { axe } from 'vitest-axe'

import { FORMAT_ISO_DATE_ONLY } from 'utils/date'
import { priceCategoryFactory } from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { RecurrenceForm } from '../RecurrenceForm'

const mockSubmit = vi.fn()

const defaultProps = {
  setIsOpen: vi.fn(),
  handleSubmit: mockSubmit,
  priceCategories: [priceCategoryFactory()],
  idLabelledBy: 'some id',
}

describe('RecurrenceForm', () => {
  it('should pass axe accessibility tests', async () => {
    const { container } = renderWithProviders(
      <RecurrenceForm {...defaultProps} />
    )
    expect(await axe(container)).toHaveNoViolations()
  })

  it('should submit', async () => {
    renderWithProviders(<RecurrenceForm {...defaultProps} />)

    await userEvent.type(
      screen.getByLabelText('Date de l’évènement *'),
      format(addDays(new Date(), 1), FORMAT_ISO_DATE_ONLY)
    )
    await userEvent.type(screen.getByLabelText('Horaire 1 *'), '12:00')
    await userEvent.type(screen.getByLabelText('Nombre de places'), '10')
    await userEvent.type(screen.getByLabelText('Tarif *'), '21')
    await userEvent.type(
      screen.getByLabelText('Date limite de réservation', { exact: false }),
      '2'
    )

    await userEvent.click(screen.getByText('Valider'))
    expect(mockSubmit).toHaveBeenCalled()
  })

  it('should add and remove a beginning time', async () => {
    renderWithProviders(<RecurrenceForm {...defaultProps} />)

    expect(
      screen.getByRole('button', { name: 'Supprimer le créneau' })
    ).toBeDisabled()

    await userEvent.click(screen.getByText('Ajouter un créneau'))

    const deleteButton = screen.getAllByRole('button', {
      name: 'Supprimer le créneau',
    })[0]
    expect(deleteButton).toBeEnabled()

    await userEvent.click(deleteButton)

    expect(
      screen.getByRole('button', { name: 'Supprimer le créneau' })
    ).toBeDisabled()
  })

  it('should show an add button until we have less or an equal number of fields than different price_categories', async () => {
    const priceCategories = [
      priceCategoryFactory(),
      priceCategoryFactory(),
      priceCategoryFactory(),
    ]
    renderWithProviders(
      <RecurrenceForm {...defaultProps} priceCategories={priceCategories} />
    )

    await userEvent.click(screen.getByText('Ajouter d’autres places et tarifs'))
    const deleteButton = screen.getAllByRole('button', {
      name: 'Supprimer les places',
    })[0]
    expect(deleteButton).toBeEnabled()
    await userEvent.click(screen.getByText('Ajouter d’autres places et tarifs'))
    expect(
      screen.queryByText('Ajouter d’autres places et tarifs')
    ).not.toBeInTheDocument()

    await userEvent.click(deleteButton)
    await userEvent.click(deleteButton)

    expect(
      screen.getByRole('button', { name: 'Supprimer les places' })
    ).toBeDisabled()
  })

  it('should render for daily recurrence', async () => {
    renderWithProviders(<RecurrenceForm {...defaultProps} />)

    await userEvent.click(screen.getByLabelText('Tous les jours'))
  })

  it('should render for weekly recurrence', async () => {
    renderWithProviders(<RecurrenceForm {...defaultProps} />)

    await userEvent.click(screen.getByLabelText('Toutes les semaines'))

    expect(screen.getByLabelText('Lundi')).toBeInTheDocument()
    expect(screen.getByLabelText('Mardi')).toBeInTheDocument()
    expect(screen.getByLabelText('Mercredi')).toBeInTheDocument()
    expect(screen.getByLabelText('Jeudi')).toBeInTheDocument()
    expect(screen.getByLabelText('Vendredi')).toBeInTheDocument()
    expect(screen.getByLabelText('Samedi')).toBeInTheDocument()
    expect(screen.getByLabelText('Dimanche')).toBeInTheDocument()
  })
})
