import React from 'react'
import { compose } from 'redux'

import OccurenceManager from '../OccurenceManager'
import withCurrentOccasion from '../hocs/withCurrentOccasion'
import withLogin from '../hocs/withLogin'
import PageWrapper from '../layout/PageWrapper'

const OccurencesPage = ({
  currentOccurences
}) => {
  return (
    <PageWrapper key={0} name="occurences">
      <OccurenceManager occurences={currentOccurences} />
    </PageWrapper>
  )
}

export default compose(
  withLogin({ isRequired: true }),
  withCurrentOccasion
)(OccurencesPage)
