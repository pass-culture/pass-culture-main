import React from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'

import OccurenceManager from '../OccurenceManager'
import withLogin from '../hocs/withLogin'
import withCurrentOccasion from '../hocs/withCurrentOccasion'
import PageWrapper from '../layout/PageWrapper'
import createSelectOccurences from '../../selectors/occurences'

const OccurencesPage = ({
  occurences
}) => {
  return (
    <PageWrapper key={0} name="occurences">
      <OccurenceManager occurences={occurences} />
    </PageWrapper>
  )
}

const selectOccurences = createSelectOccurences()

export default compose(
  withLogin({ isRequired: true }),
  withCurrentOccasion,
  connect(
    (state, ownProps) =>
      ({ occurences: selectOccurences(state, ownProps) })
  )
)(OccurencesPage)
