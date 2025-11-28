import { render } from '@testing-library/react'
import { useRef } from 'react'
import { axe } from 'vitest-axe'

import { AccessibleScrollContainer } from './AccessibleScrollContainer'

describe('<AccessibleScrollContainer />', () => {
  it('should render without accessibility violations', async () => {
    const containerRef = useRef<HTMLDivElement>(null)
    const { container } = render(
      <AccessibleScrollContainer containerRef={containerRef} liveMessage="">
        <div>Hello</div>
      </AccessibleScrollContainer>
    )

    expect(await axe(container)).toHaveNoViolations()
  })
})
