import { render, screen } from '@testing-library/react'

import FullTrashIcon from 'icons/full-trash.svg'

import {
  StockThingFormActions,
  StockThingFormActionsProps,
} from '../StockThingFormActions'
import { StockFormRowAction } from '../types'

Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: () => ({
    matches: false,
    addListener: vi.fn(),
    removeListener: vi.fn(),
  }),
})

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

  it('render actions button', () => {
    renderStockFormActions({
      actions,
    })

    const button = screen.getByRole('button', { name: 'Action label' })
    expect(button).toBeInTheDocument()
  })
})
