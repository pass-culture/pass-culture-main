import React, { createContext, useContext, useState } from 'react'

import {
  GetOffererNameResponseModel,
  GetOffererResponseModel,
} from 'apiClient/v1'

export interface ReimbursementContextValues {
  offerers: GetOffererNameResponseModel[] | null
  selectedOfferer: GetOffererResponseModel | null
  setOfferers: (offerersValues: GetOffererNameResponseModel[]) => void
  setSelectedOfferer: (offererValue: GetOffererResponseModel | null) => void
}

export const ReimbursementContext = createContext<ReimbursementContextValues>({
  offerers: null,
  selectedOfferer: null,
  setOfferers: () => {},
  setSelectedOfferer: () => {},
})

export const useReimbursementContext = () => {
  return useContext(ReimbursementContext)
}

interface ReimbursementContextProviderProps {
  children: React.ReactNode
}

export function ReimbursementContextProvider({
  children,
}: ReimbursementContextProviderProps) {
  const [offerers, setOfferers] = useState<GetOffererNameResponseModel[]>([])

  const [selectedOfferer, setSelectedOfferer] =
    useState<GetOffererResponseModel | null>(null)

  return (
    <ReimbursementContext.Provider
      value={{
        offerers,
        selectedOfferer,
        setOfferers,
        setSelectedOfferer,
      }}
    >
      {children}
    </ReimbursementContext.Provider>
  )
}
