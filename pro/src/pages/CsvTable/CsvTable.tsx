import React from 'react'

import Header from 'components/Header/Header'
import { CsvTableScreen } from 'screens/CsvTable'

import { getCsvData } from './adapters/getCsvData'

const CsvTable = (): JSX.Element => (
  <>
    <Header />
    <CsvTableScreen getCsvData={getCsvData} />
  </>
)

export default CsvTable
