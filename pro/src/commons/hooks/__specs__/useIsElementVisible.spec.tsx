import { render, screen } from '@testing-library/react'
import { useRef } from 'react'

import { useIsElementVisible } from '../useIsElementVisible'

const mockObserve = vi.fn()
const mockUnobserve = vi.fn()
const mockDisconnect = vi.fn()

interface MockedIntersectionObserverInstance {
  observe: (element: Element) => void
  unobserve: (element: Element) => void
  disconnect: () => void
  root: Element | Document | null
  rootMargin: string
  thresholds: ReadonlyArray<number>
  takeRecords: () => IntersectionObserverEntry[]
}

const MockIntersectionObserver = vi.fn(function (
  this: MockedIntersectionObserverInstance,
  _callback: IntersectionObserverCallback,
  _options?: IntersectionObserverInit
) {
  this.observe = mockObserve
  this.unobserve = mockUnobserve
  this.disconnect = mockDisconnect

  this.root = null
  this.rootMargin = '0px'
  this.thresholds = []
  this.takeRecords = vi.fn()
})
window.IntersectionObserver =
  MockIntersectionObserver as unknown as typeof IntersectionObserver

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
  it('should instanciate the observer and observe the watched element', () => {
    render(<TestComponent />)
    expect(MockIntersectionObserver).toHaveBeenCalledTimes(1)
    expect(mockObserve).toHaveBeenCalledTimes(1)
    const element = screen.getByRole('heading', { name: 'Title' })
    expect(mockObserve).toHaveBeenNthCalledWith(1, element)
  })

  it('should unobserve  on unmount', () => {
    const { unmount } = render(<TestComponent />)
    unmount()
    expect(mockDisconnect).toHaveBeenCalledTimes(1)
  })
})
