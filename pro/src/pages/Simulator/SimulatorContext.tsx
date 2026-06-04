import type { ActivityNotOpenToPublicType } from 'commons/mappings/ActivityNotOpenToPublic'
import type { ActivityOpenToPublicType } from 'commons/mappings/ActivityOpenToPublic'
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
  openToPublic: string | null
  setOpenToPublic: (openToPublic: string) => void
  activity?: ActivityOpenToPublicType | ActivityNotOpenToPublicType
  setActivity: (
    activity: ActivityOpenToPublicType | ActivityNotOpenToPublicType
  ) => void
}

export const SimulatorContext = createContext<SimulatorContextValues>({
  siret: undefined,
  setSiret: () => noop,
  targetCustomer: {
    individual: undefined,
    educational: undefined,
  },
  setTargetCustomer: () => noop,
  openToPublic: null,
  setOpenToPublic: () => noop,
  activity: undefined,
  setActivity: () => noop,
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
  const [openToPublic, setOpenToPublic] = useState<string | null>(null)
  const [activity, setActivity] = useState<
    ActivityOpenToPublicType | ActivityNotOpenToPublicType
  >()
  const [targetCustomer, setTargetCustomer] = useState<TargetCustomerObject>({
    individual: undefined,
    educational: undefined,
  })

  const contextValues: SimulatorContextValues = useMemo(
    () => ({
      siret,
      setSiret,
      targetCustomer,
      setTargetCustomer,
      openToPublic,
      setOpenToPublic,
      activity,
      setActivity,
    }),
    [siret, targetCustomer, openToPublic]
  )

  return (
    <SimulatorContext.Provider value={contextValues}>
      {children}
    </SimulatorContext.Provider>
  )
}
