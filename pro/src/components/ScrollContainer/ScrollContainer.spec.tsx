import { render } from '@testing-library/react'
import { useRef } from 'react'
import { axe } from 'vitest-axe'

import { ScrollContainer } from './ScrollContainer'

describe('<ScrollContainer />', () => {
  it('should render without accessibility violations', async () => {
    const containerRef = useRef<HTMLDivElement>(null)
    const { container } = render(
      <ScrollContainer containerRef={containerRef} liveMessage="">
        <div>Hello</div>
      </ScrollContainer>
    )

    expect(await axe(container)).toHaveNoViolations()
  })
})
