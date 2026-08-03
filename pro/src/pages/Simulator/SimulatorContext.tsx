import type React from 'react'
import { createContext, useContext, useMemo, useState } from 'react'

import type {
  ActivityNotOpenToPublic,
  ActivityOpenToPublic,
} from '@/apiClient/v1'
import { noop } from '@/commons/utils/noop'

import type { SimulatorTargetAudienceFormValues } from './SimulatorTarget/validationSchema'

export type TargetAudienceObject =
  SimulatorTargetAudienceFormValues['targetAudiences']

interface SimulatorContextValues {
  siret: string | undefined
  setSiret: (siret: string) => void
  targetAudiences: TargetAudienceObject | null
  setTargetAudiences: (targetAudiences: TargetAudienceObject) => void
  openToPublic: string | null
  setOpenToPublic: (openToPublic: string) => void
  activity?: ActivityOpenToPublic | ActivityNotOpenToPublic
  setActivity: (
    activity: ActivityOpenToPublic | ActivityNotOpenToPublic
  ) => void
}

export const SimulatorContext = createContext<SimulatorContextValues>({
  siret: undefined,
  setSiret: () => noop,
  targetAudiences: {
    individual: undefined,
    collective: undefined,
  },
  setTargetAudiences: () => noop,
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
    ActivityOpenToPublic | ActivityNotOpenToPublic
  >()
  const [targetAudiences, setTargetAudiences] = useState<TargetAudienceObject>({
    individual: undefined,
    collective: undefined,
  })

  const contextValues: SimulatorContextValues = useMemo(
    () => ({
      siret,
      setSiret,
      targetAudiences,
      setTargetAudiences,
      openToPublic,
      setOpenToPublic,
      activity,
      setActivity,
    }),
    [siret, targetAudiences, openToPublic]
  )

  return (
    <SimulatorContext.Provider value={contextValues}>
      {children}
    </SimulatorContext.Provider>
  )
}
