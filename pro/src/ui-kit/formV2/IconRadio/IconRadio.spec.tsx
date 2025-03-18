import { render, screen } from '@testing-library/react'

import { IconRadio } from './IconRadio'

describe('IconRadio', () => {
  it('should display a radio input', () => {
    render(<IconRadio label="Radio 1" icon="A" name="myField" />)

    expect(screen.getByLabelText('Radio 1')).toBeInTheDocument()
  })
})
