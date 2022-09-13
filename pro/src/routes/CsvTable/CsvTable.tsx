import React from 'react'

import Header from 'components/layout/Header/Header'
import PageTitle from 'components/layout/PageTitle/PageTitle'
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
