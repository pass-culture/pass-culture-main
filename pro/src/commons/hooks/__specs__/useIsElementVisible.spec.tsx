import { render, screen } from '@testing-library/react'
import { useRef } from 'react'

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

const disconnect = vi.fn()
const observe = vi.fn()
const unobserve = vi.fn()
describe('useIsElementVisible', () => {
  beforeEach(() => {
    window.IntersectionObserver = vi.fn().mockImplementation(() => ({
      observe,
      unobserve,
      disconnect,
    }))
  })

  it('should instanciate the observer and observe the watched element', () => {
    render(<TestComponent />)
    expect(window.IntersectionObserver).toHaveBeenCalledTimes(1)
    expect(observe).toHaveBeenCalledTimes(1)
    const element = screen.getByRole('heading', { name: 'Title' })
    expect(observe).toHaveBeenNthCalledWith(1, element)
  })

  it('should unobserve  on unmount', () => {
    const { unmount } = render(<TestComponent />)
    unmount()
    expect(disconnect).toHaveBeenCalledTimes(1)
  })
})
