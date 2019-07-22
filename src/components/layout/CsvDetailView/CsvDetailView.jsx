import PropTypes from 'prop-types'
import React, { Component } from 'react'
import Header from '../Header/Header'

class CsvDetailView extends Component {
  constructor(props) {
    super(props)
  }

  buildUniqueKey = (index, value) => {
    return `${index + '_' + value}`
  }

  printCurrentView = () => () => window.print()

  render() {
    const { currentUser, location } = this.props
    const { state } = location
    const { data, headers } = state
    const { publicName } = currentUser

    return (
      <React.Fragment>
        <Header
          isSmall
          name={publicName}
          offerers={[]}
        />
        <div id="main-container">
          <div id="csv-container">
            <table id="csv-table">
              <thead>
                <tr>
                  {headers.map((header, index) => (
                    <th key={this.buildUniqueKey(index, header)}>{header}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data.map((line, index) => (
                  <tr key={this.buildUniqueKey(index, line)}>
                    {line.map((content, index) => (
                      <td key={this.buildUniqueKey(index, content)}>{content}</td>
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
              onClick={this.printCurrentView()}
            >
              Imprimer
            </button>
          </div>
        </div>
      </React.Fragment>
    )
  }
}

CsvDetailView.propTypes = {
  currentUser: PropTypes.shape().isRequired,
  location: PropTypes.shape({
    state: PropTypes.shape().isRequired,
  }).isRequired,
}

export default CsvDetailView
