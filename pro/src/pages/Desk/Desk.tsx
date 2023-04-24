import React from 'react'

import { DeskScreen } from 'screens/Desk'

import { getBooking, submitInvalidate, submitValidate } from './adapters'

const Desk = (): JSX.Element => (
  <>
    <DeskScreen
      getBooking={getBooking}
      submitInvalidate={submitInvalidate}
      submitValidate={submitValidate}
    />
  </>
)

export default Desk
