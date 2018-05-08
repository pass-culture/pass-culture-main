import React from 'react'

import withLogin from '../hocs/withLogin'
import PageWrapper from '../layout/PageWrapper'

const NewOffererPage = () => {
  return (
    <PageWrapper name='new-offerer'>
      OOO
    </PageWrapper>
  )
}

export default withLogin({ isRequired: true })(NewOffererPage)
