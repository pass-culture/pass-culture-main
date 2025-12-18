import { renderHook } from '@testing-library/react'

import { FrontendError } from '@/commons/errors/FrontendError'

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

  it('should not focus element while loading', () => {
    const mockElement = document.createElement('input')
    mockElement.id = 'test-element'
    document.body.appendChild(mockElement)

    const focusSpy = vi.spyOn(mockElement, 'focus')

    renderHook(() => useFocusOnMounted('#test-element', true))

    expect(focusSpy).not.toHaveBeenCalled()

    mockElement.remove()
  })

  it('should focus element when loading becomes false', () => {
    const mockElement = document.createElement('input')
    mockElement.id = 'test-element'
    document.body.appendChild(mockElement)

    const focusSpy = vi.spyOn(mockElement, 'focus')

    const { rerender } = renderHook(
      ({ isLoading }) => useFocusOnMounted('#test-element', isLoading),
      { initialProps: { isLoading: true } }
    )

    expect(focusSpy).not.toHaveBeenCalled()

    rerender({ isLoading: false })

    expect(focusSpy).toHaveBeenCalledTimes(1)

    mockElement.remove()
  })

  it('should log a FrontendError when element is not found', () => {
    const consoleErrorSpy = vi
      .spyOn(console, 'error')
      .mockImplementation(() => {})

    renderHook(() => useFocusOnMounted('#non-existent-element'))

    expect(consoleErrorSpy).toHaveBeenCalledExactlyOnceWith(
      expect.any(FrontendError)
    )
  })
})
