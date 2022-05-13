import { getBooking, submitInvalidate, submitValidate } from './adapters'

import { DeskScreen } from 'screens/Desk'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import React from 'react'

const Desk = (): JSX.Element => (
  <>
    <PageTitle title="Guichet" />
    <DeskScreen
      getBooking={getBooking}
      submitInvalidate={submitInvalidate}
      submitValidate={submitValidate}
    />
  </>
)

export default Desk
