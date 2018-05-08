import React from 'react'

import withLogin from '../hocs/withLogin'
import PageWrapper from '../layout/PageWrapper'

const SettingsPage = () => {
  return (
    <PageWrapper name="réglages">
      Réglages
    </PageWrapper>
  )
}

export default withLogin({ isRequired: true })(SettingsPage)
