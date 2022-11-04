import React from 'react'

import PageTitle from 'components/PageTitle/PageTitle'
import { DeskScreen } from 'screens/Desk'

import { getBooking, submitInvalidate, submitValidate } from './adapters'

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
