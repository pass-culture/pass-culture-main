import PropTypes from 'prop-types'
import React, { Component } from 'react'
import Header from '../Header/Header'

class CsvDetailView extends Component {
  constructor(props) {
    super(props)
  }

  printCurrentView = () => () => window.print()

  render() {
    const {currentUser, location} = this.props
    const {state} = location
    const {data, headers} = state
    const {publicName} = currentUser

    return (
      <React.Fragment>
        <Header
          name={publicName}
          offerers={[]}
        />
        <div id="main-container">
          <div id="csv-container">
            <table id="csv-table">
              <thead>
              <tr>
                {headers.map(header => (
                  <th>
                    {header}
                  </th>
                ))}
              </tr>
              </thead>
              <tbody>
              {data.map(line => (
                  <tr>
                    {line.map(content => (
                      <td>
                        {content}
                      </td>
                    ))}
                  </tr>
                )
              )}
              </tbody>
            </table>
          </div>
          <hr/>
          <div id="csv-print-container">
            <button
              id="csv-print-button"
              className="button is-primary"
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
  location: PropTypes.shape({
    state: PropTypes.shape({
      detail: PropTypes.shape().isRequired
    }).isRequired
  }).isRequired,
}

export default CsvDetailView
