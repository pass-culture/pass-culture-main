import { render, screen } from '@testing-library/react'

import { Tooltip } from '../Tooltip'

describe('Tooltip', () => {
  it('should render without error', () => {
    render(
      <Tooltip visuallyHidden={false} content="Contenu du tooltip">
        Enfant
      </Tooltip>
    )

    expect(screen.getByText('Enfant')).toBeInTheDocument()
  })
})
