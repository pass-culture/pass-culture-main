import React from 'react'

import HeaderContainer from 'components/layout/Header/HeaderContainer'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import { CsvTableScreen } from 'screens/CsvTable'

import { getCsvData } from './adapters/getCsvData'

const CsvTable = (): JSX.Element => (
  <>
    <PageTitle title="Liste de vos remboursements" />
    <HeaderContainer />
    <CsvTableScreen getCsvData={getCsvData} />
  </>
)

export default CsvTable
