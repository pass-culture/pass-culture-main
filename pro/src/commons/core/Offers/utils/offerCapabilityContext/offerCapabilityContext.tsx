import { createContext, type ReactNode, useContext } from 'react'

import type { FieldEnum } from '@/apiClient/v1'

export const hasCapability = (capabilities: FieldEnum[], name: FieldEnum) =>
  capabilities.includes(name)

const CapabilityContext = createContext<FieldEnum[]>([])

export const OfferCapabilityProvider = ({
  capabilities,
  children,
}: {
  capabilities: FieldEnum[]
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
  name: FieldEnum
  children: ReactNode
}) => {
  const capabilities = useContext(CapabilityContext)

  if (!hasCapability(capabilities, name)) {
    return null
  }

  return <>{children}</>
}
