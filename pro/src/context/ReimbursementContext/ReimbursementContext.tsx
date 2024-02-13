import React, { createContext, useContext, useState } from 'react'

import { GetOffererResponseModel } from 'apiClient/v1'

export interface ReimbursementContextValues {
  selectedOfferer: GetOffererResponseModel | null
  setSelectedOfferer: (offererValue: GetOffererResponseModel | null) => void
}

export const ReimbursementContext = createContext<ReimbursementContextValues>({
  selectedOfferer: null,
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
  const [selectedOfferer, setSelectedOfferer] =
    useState<GetOffererResponseModel | null>(null)

  return (
    <ReimbursementContext.Provider
      value={{
        selectedOfferer,
        setSelectedOfferer,
      }}
    >
      {children}
    </ReimbursementContext.Provider>
  )
}
