import { useCallback } from 'react'
import { useSearchParams } from 'react-router'

const OPEN_VALUE = 'open'

export function useUrlDialogState(
  key: string
): [boolean, (open: boolean) => void] {
  const [searchParams, setSearchParams] = useSearchParams()

  const isOpen = searchParams.get(key) === OPEN_VALUE

  const setIsOpen = useCallback(
    (open: boolean) => {
      const next = new URLSearchParams(searchParams)
      if (open) {
        next.set(key, OPEN_VALUE)
        setSearchParams(next)
      } else {
        next.delete(key)
        setSearchParams(next, { replace: true })
      }
    },
    [searchParams, setSearchParams, key]
  )

  return [isOpen, setIsOpen]
}
