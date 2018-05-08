import React from 'react'

import withLogin from '../hocs/withLogin'
import PageWrapper from '../layout/PageWrapper'

const NewOfferPage = () => {
  return (
    <PageWrapper name="new-offer">
      OOO
    </PageWrapper>
  )
}

export default withLogin({ isRequired: true })(NewOfferPage)
