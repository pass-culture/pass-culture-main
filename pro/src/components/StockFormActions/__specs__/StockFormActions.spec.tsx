import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import TrashFilledIcon from 'icons/ico-trash-filled.svg'

import StockFormActions, { IStockFormActionsProps } from '../StockFormActions'
import { IStockFormRowAction } from '../types'

const renderStockFormActions = (props: IStockFormActionsProps) => {
  return render(<StockFormActions {...props} />)
}

describe('StockFormActions', () => {
  let actions: IStockFormRowAction[]
  const mockActionCallback = jest.fn()
  beforeEach(() => {
    actions = [
      {
        callback: mockActionCallback,
        label: 'Action label',
        Icon: () => (
          <TrashFilledIcon data-testid="stock-form-actions-action-icon" />
        ),
      },
    ]
  })

  it('render actions button open', () => {
    renderStockFormActions({
      actions,
    })

    expect(
      screen.getByTestId('stock-form-actions-button-open')
    ).toBeInTheDocument()
    expect(screen.getByText('Action label')).not.toBeVisible()
  })

  it('render actions list', async () => {
    renderStockFormActions({
      actions,
    })
    await userEvent.click(screen.getByTestId('stock-form-actions-button-open'))
    expect(screen.getByText('Action label')).toBeInTheDocument()
    expect(
      screen.getByTestId('stock-form-actions-action-icon')
    ).toBeInTheDocument()
  })
})
