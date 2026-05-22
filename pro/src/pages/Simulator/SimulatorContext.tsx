import type React from 'react'
import { createContext, useContext, useMemo, useState } from 'react'

import { noop } from '@/commons/utils/noop'

interface SimulatorContextValues {
  siret: string | undefined
  setSiret: (siret: string) => void
}

export const SimulatorContext = createContext<SimulatorContextValues>({
  siret: undefined,
  setSiret: () => noop,
})

export const useSimulatorContext = () => {
  return useContext(SimulatorContext)
}

interface SimulatorContextProviderProps {
  children: React.ReactNode
}

export function SimulatorContextProvider({
  children,
}: Readonly<SimulatorContextProviderProps>) {
  const [siret, setSiret] = useState<string>()

  const contextValue = useMemo(
    () => ({
      siret,
      setSiret,
    }),
    [siret]
  )

  return (
    <SimulatorContext.Provider value={contextValue}>
      {children}
    </SimulatorContext.Provider>
  )
}
