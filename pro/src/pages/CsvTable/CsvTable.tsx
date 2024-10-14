import React from 'react'

import { getCsvData } from './adapters/getCsvData'
import { CsvTableScreen } from './components/CsvTable/CsvTable'

const CsvTable = (): JSX.Element => {
  return (
    <>
      <CsvTableScreen getCsvData={getCsvData} />
    </>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = CsvTable
