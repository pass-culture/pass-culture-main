import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'jest-axe'
import React from 'react'

import { individualOfferFactory } from 'utils/individualApiFactories'

import { RecurrenceForm } from '../RecurrenceForm'

const defaultProps = {
  offer: individualOfferFactory({ stocks: [] }),
  onCancel: jest.fn(),
  onConfirm: jest.fn(),
}

describe('RecurrenceForm', () => {
  it('should pass axe accessibility tests', async () => {
    const { container } = render(<RecurrenceForm {...defaultProps} />)
    expect(await axe(container)).toHaveNoViolations()
  })

  it('should submit', async () => {
    const onConfirm = jest.fn()
    render(<RecurrenceForm {...defaultProps} onConfirm={onConfirm} />)

    await userEvent.click(
      screen.getByLabelText('Date de l’évènement', { exact: true })
    )
    await userEvent.click(screen.getByText(new Date().getDate()))
    await userEvent.click(screen.getByLabelText('Horaire 1'))
    await userEvent.click(screen.getByText('12:00'))
    await userEvent.type(screen.getByLabelText('Nombre de places'), '10')
    await userEvent.type(screen.getByLabelText('Tarif'), '21')
    await userEvent.type(
      screen.getByLabelText('Date limite de réservation', { exact: false }),
      '2'
    )

    await userEvent.click(screen.getByText('Ajouter cette date'))
    expect(onConfirm).toHaveBeenCalled()
  })

  it('should add and remove a beginning time', async () => {
    render(<RecurrenceForm {...defaultProps} />)

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

  it('should add and remove a price category', async () => {
    render(<RecurrenceForm {...defaultProps} />)

    expect(
      screen.getByRole('button', { name: 'Supprimer les places' })
    ).toBeDisabled()

    await userEvent.click(screen.getByText('Ajouter d’autres places et tarifs'))

    const deleteButton = screen.getAllByRole('button', {
      name: 'Supprimer les places',
    })[0]
    expect(deleteButton).toBeEnabled()

    await userEvent.click(deleteButton)

    expect(
      screen.getByRole('button', { name: 'Supprimer les places' })
    ).toBeDisabled()
  })

  it('should render for daily recurrence', async () => {
    render(<RecurrenceForm {...defaultProps} />)

    await userEvent.click(screen.getByLabelText('Tous les jours'))
  })
})
