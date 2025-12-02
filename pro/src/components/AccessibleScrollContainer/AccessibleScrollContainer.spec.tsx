import { render, screen } from '@testing-library/react'
import { createRef } from 'react'
import { expect } from 'vitest'
import { axe } from 'vitest-axe'

import { AccessibleScrollContainer } from './AccessibleScrollContainer'

const renderComponent = () => {
  const containerRef = createRef<HTMLDivElement>()
  return render(
    <AccessibleScrollContainer
      containerRef={containerRef}
      liveMessage="This is a vocal annoucement"
    >
      <div>This is a visual content</div>
    </AccessibleScrollContainer>
  )
}

describe('<AccessibleScrollContainer />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderComponent()

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should have the live message', () => {
    renderComponent()

    expect(
      screen.getByRole('status', { name: 'This is a vocal annoucement' })
    ).toBeInTheDocument()

    expect(screen.getByText('This is a visual content')).toBeInTheDocument()
  })
})
