import { render, screen } from '@testing-library/react'

import { ToggleButtonGroup } from '../ToggleButtonGroup'

describe('ToggleButtonGroup', () => {
  it('should set active styles on the active button', () => {
    render(
      <ToggleButtonGroup
        buttons={[
          {
            id: 'id 1',
            label: 'label 1',
            content: <>test 1</>,
            onClick: () => {},
          },
          {
            id: 'id 2',
            label: 'label 2',
            content: <>test 2</>,
            onClick: () => {},
          },
        ]}
        activeButton="id 2"
        groupLabel="Nom du groupe"
      />
    )

    expect(screen.getByRole('button', { name: 'label 1' })).not.toHaveClass(
      'button-group-button-active'
    )
    expect(screen.getByRole('button', { name: 'label 2' })).toHaveClass(
      'button-group-button-active'
    )
  })
})
