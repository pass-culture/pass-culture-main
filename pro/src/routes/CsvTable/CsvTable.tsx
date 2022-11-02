import React from 'react'

import { Header } from 'new_components/Header'
import { PageTitle } from 'new_components/PageTitle'
import { CsvTableScreen } from 'screens/CsvTable'

import { getCsvData } from './adapters/getCsvData'

const CsvTable = (): JSX.Element => (
  <>
    <PageTitle title="Liste de vos remboursements" />
    <Header />
    <CsvTableScreen getCsvData={getCsvData} />
  </>
)

export default CsvTable
