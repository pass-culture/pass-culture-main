import { createContext, useContext, useMemo, useState } from 'react'

import { noop } from '@/commons/utils/noop'

type SkipLinksContextValue = {
  menuContainer: HTMLLIElement | null
  setMenuContainer: (node: HTMLLIElement | null) => void
  footerContainer: HTMLLIElement | null
  setFooterContainer: (node: HTMLLIElement | null) => void
}

const SkipLinksContext = createContext<SkipLinksContextValue>({
  menuContainer: null,
  setMenuContainer: noop,
  footerContainer: null,
  setFooterContainer: noop,
})

export const useSkipLinksContext = () => useContext(SkipLinksContext)

type SkipLinksProviderProps = {
  children: React.ReactNode
}

export function SkipLinksProvider({
  children,
}: Readonly<SkipLinksProviderProps>) {
  const [menuContainer, setMenuContainer] = useState<HTMLLIElement | null>(null)
  const [footerContainer, setFooterContainer] = useState<HTMLLIElement | null>(
    null
  )

  const contextValue = useMemo(
    () => ({
      menuContainer,
      footerContainer,
      setMenuContainer,
      setFooterContainer,
    }),
    [menuContainer, footerContainer]
  )

  return (
    <SkipLinksContext.Provider value={contextValue}>
      {children}
    </SkipLinksContext.Provider>
  )
}
