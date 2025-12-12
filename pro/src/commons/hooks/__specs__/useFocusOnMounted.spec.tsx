import { renderHook } from '@testing-library/react'

import { useFocusOnMounted } from '../useFocusOnMounted'

describe('useFocusOnMounted()', () => {
  it('should focus element by selector when mounted', () => {
    const mockElement = document.createElement('input')
    mockElement.id = 'test-element'
    document.body.appendChild(mockElement)

    const focusSpy = vi.spyOn(mockElement, 'focus')

    renderHook(() => useFocusOnMounted('#test-element'))

    expect(focusSpy).toHaveBeenCalledTimes(1)

    mockElement.remove()
  })

  it('should focus element by HTMLElement reference when mounted', () => {
    const mockElement = document.createElement('input')
    document.body.appendChild(mockElement)

    const focusSpy = vi.spyOn(mockElement, 'focus')

    renderHook(() => useFocusOnMounted(mockElement))

    expect(focusSpy).toHaveBeenCalledTimes(1)

    mockElement.remove()
  })

  it('should not throw when element is not found', () => {
    expect(() => {
      renderHook(() => useFocusOnMounted('#non-existent-element'))
    }).not.toThrow()
  })
})
