import React from 'react'

import PageTitle from 'components/layout/PageTitle/PageTitle'
import Titles from 'components/layout/Titles/Titles'

import styles from './BusinessUnitList.module.scss'

const BusinessUnitList = (): JSX.Element => {
  return (
    <div className={styles['business-unit-page']}>
      <PageTitle title="Points de facturations" />
      <Titles title="Points de facturations" />
    </div>
  )
}

export default BusinessUnitList
