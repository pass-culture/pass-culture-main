import { createContext, type ReactNode, useContext } from 'react'

const CapabilityContext = createContext<string[]>([])

export const OfferCapabilityProvider = ({
  capabilities,
  children,
}: {
  capabilities: string[]
  children: ReactNode
}) => (
  <CapabilityContext.Provider value={capabilities}>
    {children}
  </CapabilityContext.Provider>
)

export const HasCapability = ({
  name,
  children,
}: {
  name: string
  children: ReactNode
}) => {
  const capabilities = useContext(CapabilityContext)

  if (!capabilities.includes(name)) {
    return null // N'affiche rien si l'offre n'a pas la capacité
  }

  return <>{children}</>
}
