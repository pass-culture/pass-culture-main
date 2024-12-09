import { render, screen } from '@testing-library/react'

import {
  FieldLayoutCharacterCount,
  FieldLayoutCharacterCountProps,
} from './FieldLayoutCharacterCount'

describe('FieldLayoutCharacterCount', () => {
  const props: FieldLayoutCharacterCountProps = {
    count: 10,
    maxLength: 100,
    name: 'field',
  }
  it('should show the count of characters typed', () => {
    render(<FieldLayoutCharacterCount {...props} />)

    expect(screen.getByText('10/100')).toBeInTheDocument()
  })

  it('should have a count of characters for assistive technologies taht is visually hidden', () => {
    render(<FieldLayoutCharacterCount {...props} />)

    const counter = screen.getByText('10 caractères sur 100')
    expect(counter).toBeInTheDocument()

    //  Check that the visually-hidden mixin is applied
    expect(counter).toHaveClass(/visually-hidden/)
  })

  it('should delay the change of the count for the hidden counter', () => {
    const { rerender } = render(<FieldLayoutCharacterCount {...props} />)
    expect(screen.getByText('10/100')).toBeInTheDocument()
    expect(screen.getByText('10 caractères sur 100')).toBeInTheDocument()

    rerender(<FieldLayoutCharacterCount {...props} count={11} />)

    expect(screen.getByText('11/100')).toBeInTheDocument()
    expect(screen.getByText('10 caractères sur 100')).toBeInTheDocument()
  })
})
