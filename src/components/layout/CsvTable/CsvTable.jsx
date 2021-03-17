import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'

import Header from '../Header/Header'
import PageTitle from '../PageTitle/PageTitle'
import Spinner from '../Spinner'

class CsvTable extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      dataFromCsv: {},
      isLoading: true,
    }
  }

  async componentDidMount() {
    await this.getCsvData()
  }

  async getCsvData() {
    const { downloadFileOrNotifyAnError } = this.props
    const dataFromCsv = await downloadFileOrNotifyAnError()
    this.setState({
      dataFromCsv: dataFromCsv,
      isLoading: false,
    })
  }

  buildUniqueKey = (index, value) => `${index + '_' + value}`

  handlePrintCurrentView = () => window.print()

  render() {
    const { currentUser } = this.props
    const { dataFromCsv, isLoading } = this.state
    const { data = [], headers = [] } = dataFromCsv
    const { publicName } = currentUser
    const hasAtLeastData = data.length > 0

    return (
      <>
        <PageTitle title="Liste de vos remboursements" />
        <Header
          name={publicName}
          offerers={[]}
        />
        {isLoading && (
          <div id="spinner-container">
            <Spinner />
          </div>
        )}

        {hasAtLeastData && !isLoading && (
          <main id="main-container">
            <div id="csv-container">
              <table id="csv-table">
                <thead>
                  <tr>
                    {headers.map((header, index) => (
                      <th key={this.buildUniqueKey(index, header)}>
                        {header}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {data &&
                    data.map((line, index) => (
                      <tr key={this.buildUniqueKey(index, line)}>
                        {line.map((content, index) => (
                          <td key={this.buildUniqueKey(index, content)}>
                            {content}
                          </td>
                        ))}
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
            <hr />
            <div id="csv-print-container">
              <button
                className="button is-primary"
                id="csv-print-button"
                onClick={this.handlePrintCurrentView}
                type="button"
              >
                {'Imprimer'}
              </button>
            </div>
          </main>
        )}

        {!hasAtLeastData && !isLoading && (
          <main className="no-data-container">
            <p>
              {`Il n'y a pas de données à afficher.`}
            </p>
          </main>
        )}
      </>
    )
  }
}

CsvTable.propTypes = {
  currentUser: PropTypes.shape().isRequired,
  downloadFileOrNotifyAnError: PropTypes.func.isRequired,
}

export default CsvTable
