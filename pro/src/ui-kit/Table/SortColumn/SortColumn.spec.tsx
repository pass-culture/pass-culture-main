import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'

import { SortingMode } from 'commons/hooks/useColumnSorting'

import { SortColumn } from './SortColumn'

describe('<SortColumn />', () => {
  it('renders children content', () => {
    render(
      <SortColumn sortingMode={SortingMode.NONE} onClick={() => {}}>
        My Column
      </SortColumn>
    )
    expect(screen.getByText('My Column')).toBeInTheDocument()
  })

  it('renders up icon when sortingMode is DESC', () => {
    render(
      <SortColumn sortingMode={SortingMode.DESC} onClick={() => {}}>
        Label
      </SortColumn>
    )
    expect(screen.getByLabelText('Ne plus trier')).toBeInTheDocument()
  })

  it('renders down icon when sortingMode is ASC', () => {
    render(
      <SortColumn sortingMode={SortingMode.ASC} onClick={() => {}}>
        Label
      </SortColumn>
    )
    expect(
      screen.getByLabelText('Trier par ordre décroissant')
    ).toBeInTheDocument()
  })

  it('calls onClick when clicked', async () => {
    const onClick = vi.fn()
    const user = userEvent.setup()

    render(
      <SortColumn sortingMode={SortingMode.NONE} onClick={onClick}>
        Clickable
      </SortColumn>
    )
    const button = screen.getByRole('button', { name: /clickable/i })
    await user.click(button)

    expect(onClick).toHaveBeenCalledTimes(1)
  })
})
