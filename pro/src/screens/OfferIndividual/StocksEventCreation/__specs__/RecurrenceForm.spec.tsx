import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { individualOfferFactory } from 'utils/individualApiFactories'

import { RecurrenceForm } from '../RecurrenceForm'

const defaultProps = {
  offer: individualOfferFactory({ stocks: [] }),
  onCancel: jest.fn(),
  onConfirm: jest.fn(),
}

describe('RecurrenceForm', () => {
  it('should submit', async () => {
    const onConfirm = jest.fn()
    render(<RecurrenceForm {...defaultProps} onConfirm={onConfirm} />)

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
})
