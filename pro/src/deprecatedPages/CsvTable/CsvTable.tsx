import React from 'react'

import Header from 'components/Header/Header'
import PageTitle from 'components/PageTitle/PageTitle'
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
