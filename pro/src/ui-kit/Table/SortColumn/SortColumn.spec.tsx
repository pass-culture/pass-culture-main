import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'

import { SortingMode } from '@/commons/hooks/useColumnSorting'

import { SortColumn } from './SortColumn'
import styles from './SortColumn.module.scss'

describe('<SortColumn />', () => {
  it.each([
    {
      sortingMode: SortingMode.NONE,
      action: 'Cliquez pour trier par ordre croissant',
      description: 'Aucun tri appliqué à cette colonne.',
    },
    {
      sortingMode: SortingMode.ASC,
      action: 'Cliquez pour trier par ordre décroissant',
      description: 'Tri actuel : ordre croissant.',
    },
    {
      sortingMode: SortingMode.DESC,
      action: 'Cliquez pour ne plus trier',
      description: 'Tri actuel : ordre décroissant.',
    },
  ])(
    'exposes the current sorting state separately from the next action in $sortingMode mode',
    ({ sortingMode, action, description }) => {
      render(
        <SortColumn sortingMode={sortingMode} onClick={() => {}}>
          My Column
        </SortColumn>
      )

      expect(
        screen.getByRole('button', { name: `My Column ${action}` })
      ).toHaveAccessibleDescription(description)
      expect(screen.getByText(description)).toHaveClass(
        styles['visually-hidden']
      )
    }
  )

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
    expect(
      screen.getByLabelText('Cliquez pour ne plus trier')
    ).toBeInTheDocument()
  })

  it('renders down icon when sortingMode is ASC', () => {
    render(
      <SortColumn sortingMode={SortingMode.ASC} onClick={() => {}}>
        Label
      </SortColumn>
    )
    expect(
      screen.getByLabelText('Cliquez pour trier par ordre décroissant')
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
