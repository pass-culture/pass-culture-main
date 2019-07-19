import { connect } from 'react-redux'

import DisplayButton from './DisplayButton'
import { showNotification } from 'pass-culture-shared'
import csvConverter from './utils/csvConverter'
import { compose } from 'redux'
import { withRouter } from 'react-router-dom'

export const mapDispatchToProps = (dispatch, ownProps) => {
  const {href} = ownProps

  return {
    downloadFileOrNotifyAnError: async () => {
      try {
        const result = await fetch(href, {credentials: 'include'})
        const {status} = result

        if (status === 200) {
          const text = await result.text()
          return csvConverter(text)
        }

        dispatch(
          showNotification({
            text: 'Il y a une erreur avec le chargement des données',
            type: 'danger',
          })
        )
      } catch (error) {
        console.log('error', error)
      }
    },
    showFailureNotification: () => {
      dispatch(
        showNotification({
          text: 'Il n\'y a pas de données à afficher.',
          type: 'danger',
        })
      )
    }
  }
}

export default compose(
  withRouter,
  connect(
    null,
    mapDispatchToProps
  )
)(DisplayButton)
