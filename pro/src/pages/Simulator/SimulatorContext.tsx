import type React from 'react'
import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
} from 'react'

import {
  LOCAL_STORAGE_KEY,
  localStorageManager,
} from '@/commons/utils/localStorageManager'
import { noop } from '@/commons/utils/noop'

interface SimulatorContextValues {
  siret: string | undefined
  setSiretAndSave: (siret: string) => void
}

export const SimulatorContext = createContext<SimulatorContextValues>({
  siret: undefined,
  setSiretAndSave: () => noop,
})

export const useSimulatorContext = () => {
  return useContext(SimulatorContext)
}

interface SimulatorContextProviderProps {
  children: React.ReactNode
}

const saveSiretToStorage = (siret: string) => {
  localStorageManager.setItem(LOCAL_STORAGE_KEY.SIMULATOR_SIRET, siret)
}

export function SimulatorContextProvider({
  children,
}: Readonly<SimulatorContextProviderProps>) {
  const [siret, setSiret] = useState<string>()

  const setSiretAndSave = useCallback((siret: string) => {
    setSiret(siret)
    saveSiretToStorage(siret)
  }, [])

  const contextValue = useMemo(
    () => ({
      siret,
      setSiretAndSave,
    }),
    [siret, setSiretAndSave]
  )

  return (
    <SimulatorContext.Provider value={contextValue}>
      {children}
    </SimulatorContext.Provider>
  )
}
