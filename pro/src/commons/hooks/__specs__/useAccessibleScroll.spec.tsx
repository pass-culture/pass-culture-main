import { renderHook } from '@testing-library/react'

import { useMediaQuery } from '@/commons/hooks/useMediaQuery'

import { useAccessibleScroll } from '../useAccessibleScroll'

vi.mock('@/commons/hooks/useMediaQuery', () => ({
  useMediaQuery: vi.fn(() => false),
}))

const createMockRect = (top: number) => new DOMRect(0, top, 0, 0)

describe('useAccessibleScroll', () => {
  it('should scroll to the content wrapper on the window', () => {
    const windowScrollSpy = vi
      .spyOn(globalThis.window, 'scrollTo')
      .mockImplementation(() => {})
    Object.defineProperty(globalThis.window, 'scrollY', {
      configurable: true,
      value: 60,
      writable: true,
    })

    const { result } = renderHook(() => useAccessibleScroll())

    // Faking a content wrapper element
    const focus = vi.fn()
    const contentElement = {
      focus,
      getBoundingClientRect: vi.fn(() => createMockRect(180)),
    } as unknown as HTMLDivElement

    // @ts-expect-error: Refs normally attached on components, but we need here to attach it to the mocked content element for the test
    result.current.contentWrapperRef.current = contentElement
    result.current.scrollToContentWrapper()

    expect(focus).toHaveBeenCalledTimes(1)
    expect(windowScrollSpy).toHaveBeenCalledWith({
      top: 240,
      behavior: 'smooth',
    })

    windowScrollSpy.mockRestore()
  })

  it('should scroll inside the provided selector when available', () => {
    const windowScrollSpy = vi
      .spyOn(globalThis.window, 'scrollTo')
      .mockImplementation(() => {})
    const querySelectorSpy = vi
      .spyOn(document, 'querySelector')
      .mockImplementation(() => null)
    vi.mocked(useMediaQuery).mockReturnValueOnce(true)

    // Create and set up a mock containing page wrapper
    const pageWrapper = document.createElement('div')
    pageWrapper.scrollTop = 30

    // Mock the scrollTo method on this wrapper
    const pageScrollSpy = vi.fn()
    Object.defineProperty(pageWrapper, 'scrollTo', {
      configurable: true,
      value: pageScrollSpy,
      writable: true,
    })

    vi.spyOn(pageWrapper, 'getBoundingClientRect').mockReturnValue(
      createMockRect(40)
    )
    // Make querySelector return the pageWrapper mock
    querySelectorSpy.mockReturnValue(pageWrapper)

    // Render the hook with a selector option
    const { result } = renderHook(() =>
      useAccessibleScroll({
        selector: '#page-wrapper',
      })
    )

    // Mock the content element to represent the scroll target
    const focus = vi.fn()
    const contentElement = {
      focus,
      getBoundingClientRect: vi.fn(() => createMockRect(180)),
    } as unknown as HTMLDivElement

    // Attach mocked content element to the hook ref
    // @ts-expect-error: Refs normally attached on components, but we need here to attach it to the mocked content element for the test
    result.current.contentWrapperRef.current = contentElement
    result.current.scrollToContentWrapper()

    expect(querySelectorSpy).toHaveBeenCalledWith('#page-wrapper')
    expect(pageScrollSpy).toHaveBeenCalledWith({
      top: 170,
      behavior: 'instant',
    })
    expect(windowScrollSpy).not.toHaveBeenCalled()

    windowScrollSpy.mockRestore()
    querySelectorSpy.mockRestore()
  })
})
