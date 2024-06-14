import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import FullTrashIcon from 'icons/full-trash.svg'

import {
  StockThingFormActions,
  StockThingFormActionsProps,
} from '../StockThingFormActions'
import { StockFormRowAction } from '../types'

const renderStockFormActions = (props: StockThingFormActionsProps) => {
  return render(<StockThingFormActions {...props} />)
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
    expect(screen.getAllByText('Action label')).toHaveLength(1)
  })

  it('render actions list', async () => {
    renderStockFormActions({
      actions,
    })
    await userEvent.click(screen.getByTestId('dropdown-menu-trigger'))
    expect(screen.getAllByText('Action label')).toHaveLength(2)
  })
})
