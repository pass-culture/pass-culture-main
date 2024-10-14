import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import FullTrashIcon from 'icons/full-trash.svg'

import {
  StockEventFormActions,
  StockEventFormActionsProps,
} from '../StockEventFormActions'
import { StockFormRowAction } from '../types'

const renderStockFormActions = (props: StockEventFormActionsProps) => {
  return render(<StockEventFormActions {...props} />)
}

describe('StockFormActions', () => {
  let actions: StockFormRowAction[]
  const mockActionCallback = vi.fn()
  beforeEach(() => {
    actions = [
      {
        callback: mockActionCallback,
        label: 'Action label',
        icon: FullTrashIcon,
      },
    ]
  })

  it('render actions button open', () => {
    renderStockFormActions({
      actions,
    })

    expect(screen.getByTestId('dropdown-menu-trigger')).toBeInTheDocument()
    expect(screen.queryByText('Action label')).not.toBeInTheDocument()
  })

  it('render actions list', async () => {
    renderStockFormActions({
      actions,
    })
    await userEvent.click(screen.getByTestId('dropdown-menu-trigger'))
    expect(screen.getByText('Action label')).toBeInTheDocument()
  })
})
