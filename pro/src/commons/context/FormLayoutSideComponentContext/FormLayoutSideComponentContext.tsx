import { createContext, useContext } from 'react'

const FormLayoutSideComponentContext = createContext<string | undefined>(
  undefined
)

type FormLayoutSideComponentContextProviderProps = {
  children: React.ReactNode
  describedById: string
}

export const FormLayoutSideComponentContextProvider = ({
  children,
  describedById,
}: Readonly<FormLayoutSideComponentContextProviderProps>) => {
  return (
    <FormLayoutSideComponentContext.Provider value={describedById}>
      {children}
    </FormLayoutSideComponentContext.Provider>
  )
}

export const useFormLayoutSideComponentDescribedBy = () => {
  return useContext(FormLayoutSideComponentContext)
}
