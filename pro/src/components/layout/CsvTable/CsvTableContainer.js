import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import csvConverter from '../CsvTableButton/utils/csvConverter'

import CsvTable from './CsvTable'

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

export default compose(withRouter, connect(null, mapDispatchToProps))(CsvTable)
