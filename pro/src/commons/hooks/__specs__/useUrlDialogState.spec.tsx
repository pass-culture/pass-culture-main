import { act, renderHook } from '@testing-library/react'
import type { ReactNode } from 'react'
import { MemoryRouter, useLocation } from 'react-router'

import { useUrlDialogState } from '../useUrlDialogState'

const renderUseUrlDialogState = (key: string, url: string = '/') => {
  const locations: string[] = []
  function LocationSpy() {
    const location = useLocation()
    locations.push(`${location.pathname}${location.search}`)
    return null
  }

  const wrapper = ({ children }: { children: ReactNode }) => (
    <MemoryRouter initialEntries={[url]}>
      {children}
      <LocationSpy />
    </MemoryRouter>
  )

  const { result, ...rest } = renderHook(() => useUrlDialogState(key), {
    wrapper,
  })

  return {
    ...rest,
    locations,
    get isOpen() {
      return result.current[0]
    },
    setIsOpen: (open: boolean) => result.current[1](open),
  }
}

describe('useUrlDialogState', () => {
  it('returns false when the URL does not contain the key', () => {
    const { isOpen } = renderUseUrlDialogState('dialog', '/page')
    expect(isOpen).toBe(false)
  })

  it('returns true when the URL contains key=open', () => {
    const { isOpen } = renderUseUrlDialogState('dialog', '/page?dialog=open')
    expect(isOpen).toBe(true)
  })

  it('returns false when the URL contains the key with a different value', () => {
    const { isOpen } = renderUseUrlDialogState('dialog', '/page?dialog=true')
    expect(isOpen).toBe(false)
  })

  it('opens the dialog by writing the param to the URL', () => {
    const dialog = renderUseUrlDialogState('dialog', '/page')

    act(() => dialog.setIsOpen(true))

    expect(dialog.isOpen).toBe(true)
    expect(dialog.locations.at(-1)).toBe('/page?dialog=open')
  })

  it('closes the dialog by removing the param from the URL', () => {
    const dialog = renderUseUrlDialogState('dialog', '/page?dialog=open')

    act(() => dialog.setIsOpen(false))

    expect(dialog.isOpen).toBe(false)
    expect(dialog.locations.at(-1)).toBe('/page')
  })

  it('preserves other search params when opening/closing', () => {
    const dialog = renderUseUrlDialogState('dialog', '/page?foo=bar')

    act(() => dialog.setIsOpen(true))
    expect(dialog.locations.at(-1)).toBe('/page?foo=bar&dialog=open')

    act(() => dialog.setIsOpen(false))
    expect(dialog.locations.at(-1)).toBe('/page?foo=bar')
  })
})
