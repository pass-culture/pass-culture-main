import React from 'react'
import { compose } from 'redux'

import OccurenceManager from '../OccurenceManager'
import withCurrentOccasion from '../hocs/withCurrentOccasion'
import withLogin from '../hocs/withLogin'
import PageWrapper from '../layout/PageWrapper'

const OccurencesPage = props => {
  return (
    <PageWrapper name="occurences">
      <OccurenceManager {...props}/>
    </PageWrapper>
  )
}

export default compose(
  withLogin({ isRequired: true }),
  withCurrentOccasion
)(OccurencesPage)
