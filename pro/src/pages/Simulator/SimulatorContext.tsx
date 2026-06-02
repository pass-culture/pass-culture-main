import type React from 'react'
import { createContext, useContext, useMemo, useState } from 'react'

import { noop } from '@/commons/utils/noop'

import type { SimulatorTargetCustomerFormValues } from './SimulatorTarget/validationSchema'

export type TargetCustomerObject =
  SimulatorTargetCustomerFormValues['targetCustomer']

interface SimulatorContextValues {
  siret: string | undefined
  setSiret: (siret: string) => void
  targetCustomer: TargetCustomerObject | null
  setTargetCustomer: (targetCustomer: TargetCustomerObject) => void
}

export const SimulatorContext = createContext<SimulatorContextValues>({
  siret: undefined,
  setSiret: () => noop,
  targetCustomer: {
    individual: undefined,
    educational: undefined,
  },
  setTargetCustomer: () => noop,
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

  const [targetCustomer, setTargetCustomer] = useState<TargetCustomerObject>({
    individual: undefined,
    educational: undefined,
  })

  const contextValues = useMemo(
    () => ({
      siret,
      setSiret,
      targetCustomer,
      setTargetCustomer,
    }),
    [siret, targetCustomer]
  )

  return (
    <SimulatorContext.Provider value={contextValues}>
      {children}
    </SimulatorContext.Provider>
  )
}
