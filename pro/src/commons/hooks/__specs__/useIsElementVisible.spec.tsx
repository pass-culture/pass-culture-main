import { render, screen } from '@testing-library/react'
import { useRef } from 'react'
import type { Mock } from 'vitest'

import { useIsElementVisible } from '../useIsElementVisible'

const TestComponent = () => {
  const elementWatched = useRef(null)
  const [titleIsVisible] = useIsElementVisible(elementWatched)

  return (
    <main style={{ height: '1000px' }}>
      <h1 ref={elementWatched}>Title</h1>
      {!titleIsVisible && <div>Div is visible when title is not</div>}
    </main>
  )
}

describe('useIsElementVisible', () => {
  beforeEach(() => {
    vi.clearAllMocks() // Crucial to reset call counts between tests
  })

  it('should instanciate the observer and observe the watched element', () => {
    render(<TestComponent />)

    const observerInstance = (IntersectionObserver as unknown as Mock).mock
      .results[0].value
    expect(observerInstance.observe).toHaveBeenCalledTimes(1)
    const element = screen.getByRole('heading', { name: 'Title' })
    expect(observerInstance.observe).toHaveBeenNthCalledWith(1, element)
  })

  it('should unobserve  on unmount', () => {
    const { unmount } = render(<TestComponent />)
    unmount()

    const observerInstance = (IntersectionObserver as unknown as Mock).mock
      .results[0].value
    expect(observerInstance.disconnect).toHaveBeenCalledTimes(1)
  })
})
