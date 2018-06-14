import React from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'

import OccurenceManager from '../OccurenceManager'
import withLogin from '../hocs/withLogin'
import withCurrentOccasion from '../hocs/withCurrentOccasion'
import PageWrapper from '../layout/PageWrapper'
import selectEventOccurences from '../../selectors/eventOccurences'

const OccurencesPage = ({
  eventOccurences
}) => {
  return (
    <PageWrapper key={0} name="occurences">
      <OccurenceManager occurences={eventOccurences} />
    </PageWrapper>
  )
}

export default compose(
  withLogin({ isRequired: true }),
  withCurrentOccasion,
  connect(
    (state, ownProps) =>
      ({ eventOccurences: selectEventOccurences(state, ownProps) })
  )
)(OccurencesPage)
