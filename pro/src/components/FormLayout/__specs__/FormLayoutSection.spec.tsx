import { render, screen } from '@testing-library/react'

import { Section } from '../FormLayoutSection'

describe('Section', () => {
  it('should render the component', () => {
    render(<Section title={'my title'}>Hello</Section>)

    expect(screen.getByText('my title')).toBeInTheDocument()
    expect(screen.getByText('Hello')).toBeInTheDocument()
  })
})
