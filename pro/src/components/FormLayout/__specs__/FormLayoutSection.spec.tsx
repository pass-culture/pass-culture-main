import { render, screen } from '@testing-library/react'

import { Section } from '../FormLayoutSection'

describe('Section', () => {
  it('should render the component', () => {
    render(<Section title={'my title'}>Hello</Section>)

    expect(screen.getByRole('group', { name: 'my title' })).toBeInTheDocument()
    expect(screen.getByText('my title')).toBeInTheDocument()
    expect(screen.getByText('Hello')).toBeInTheDocument()
  })

  it('should render an accessible legend when the title is hidden', () => {
    render(<Section accessibleLabel="Activity details">Hello</Section>)

    expect(
      screen.getByRole('group', { name: 'Activity details' })
    ).toBeInTheDocument()
    expect(
      screen.queryByRole('heading', { name: 'Activity details' })
    ).toBeNull()
  })
})
