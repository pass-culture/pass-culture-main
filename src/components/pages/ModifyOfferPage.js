import React from 'react'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import withLogin from '../hocs/withLogin'
import PageWrapper from '../layout/PageWrapper'

const ModifyOfferPage = () => {
  return (
    <PageWrapper name="modify-offer">
      OOO
    </PageWrapper>
  )
}

export default compose(
  withLogin({ isRequired: true }),
  withRouter
)(ModifyOfferPage)
