import React from 'react'

import Header from 'components/Header/Header'
import useActiveFeature from 'hooks/useActiveFeature'
import { CsvTableScreen } from 'screens/CsvTable'

import { getCsvData } from './adapters/getCsvData'

const CsvTable = (): JSX.Element => {
  const isFFnewInterfaceActive = useActiveFeature('WIP_ENABLE_PRO_SIDE_NAV')
  return (
    <>
      {!isFFnewInterfaceActive && <Header />}
      <CsvTableScreen getCsvData={getCsvData} />
    </>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = CsvTable
