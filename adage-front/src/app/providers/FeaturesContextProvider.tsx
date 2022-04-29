import React, {
  createContext,
  ReactNode,
  useEffect,
  useMemo,
  useState,
} from 'react'

import { LoaderPage } from 'app/components/LoaderPage/LoaderPage'
import { Feature } from 'app/types'
import { getFeatures } from 'repository/pcapi/pcapi'

export type FeaturesContextType = Feature[]

export const featuresContextInitialValues: FeaturesContextType = []

export const FeaturesContext = createContext<FeaturesContextType>(
  featuresContextInitialValues
)

export const FeaturesContextProvider = ({
  children,
}: {
  children: ReactNode | ReactNode[]
}): JSX.Element => {
  const [features, setFeatures] = useState<Feature[]>([])
  const [isReady, setIsReady] = useState(false)

  useEffect(() => {
    const loadFeatures = async () => {
      const loadedFeatures = await getFeatures()
      setFeatures(loadedFeatures)
      setIsReady(true)
    }

    loadFeatures()
  }, [])

  const value = useMemo(() => features, [features])

  if (!isReady) {
    return <LoaderPage />
  }

  return (
    <FeaturesContext.Provider value={value}>
      {children}
    </FeaturesContext.Provider>
  )
}
