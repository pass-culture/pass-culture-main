import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { individualOfferFactory } from 'utils/individualApiFactories'

import { RecurrenceForm } from '../RecurrenceForm'

describe('RecurrenceForm', () => {
  it('should submit', async () => {
    const onConfirm = jest.fn()
    render(
      <RecurrenceForm
        offer={individualOfferFactory({ stocks: [] })}
        onCancel={jest.fn()}
        onConfirm={onConfirm}
      />
    )

    await userEvent.click(screen.getByText('Ajouter cette date'))
    expect(onConfirm).toHaveBeenCalled()
  })
})
