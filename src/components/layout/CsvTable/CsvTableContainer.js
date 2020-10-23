import { compose } from 'redux'
import CsvTable from './CsvTable'
import withRequiredLogin from 'components/hocs/with-login/withRequiredLogin'
import csvConverter from '../CsvTableButton/utils/csvConverter'
import { withRouter } from 'react-router-dom'
import { connect } from 'react-redux'

export const mapDispatchToProps = (dispatch, ownProps) => {
  const { location } = ownProps
  const { state: pathToCsv } = location

  return {
    downloadFileOrNotifyAnError: async () => {
      try {
        const result = await fetch(pathToCsv, { credentials: 'include' })
        const { status } = result

        if (status === 200) {
          const text = await result.text()
          return csvConverter(text)
        }
      } catch (error) {
        throw new Error('Erreur lors du téléchargement des données.')
      }
    },
  }
}

export default compose(
  withRequiredLogin,
  withRouter,
  connect(
    null,
    mapDispatchToProps
  )
)(CsvTable)
