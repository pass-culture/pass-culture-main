/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'
import ReactMarkdown from 'react-markdown'
import { Scrollbars } from 'react-custom-scrollbars'

import { ROOT_PATH, APP_VERSION } from '../../utils/config'
import PageHeader from '../layout/PageHeader'
import NavigationFooter from '../layout/NavigationFooter'

class TermsPage extends React.PureComponent {
  constructor(props) {
    super(props)
    this.state = { source: '' }
  }

  async componentDidMount() {
    const result = await fetch(`${ROOT_PATH}/MentionsLegalesPass.md`)
    const source = await result.text()
    this.setState({ source })
  }

  render() {
    const { source } = this.state
    const { appversion } = this.props
    const backgroundImage = `url('${ROOT_PATH}/mosaic-k@2x.png')`
    return (
      <div id="terms-page" className="page is-relative flex-rows">
        <PageHeader theme="red" title="Mentions légales" />
        <main role="main" className="pc-main my12">
          <Scrollbars>
            <div className="padded content" style={{ backgroundImage }}>
              <ReactMarkdown source={source} />
              <div className="mt16">
                <p>Pass Culture version v{appversion}</p>
              </div>
            </div>
          </Scrollbars>
        </main>
        <NavigationFooter theme="white" className="dotted-top-red" />
      </div>
    )
  }
}

TermsPage.defaultProps = {
  appversion: APP_VERSION,
}

TermsPage.propTypes = {
  // pass `appversion` from props
  // only for enzyme snapshots tests
  appversion: PropTypes.string,
}

export default TermsPage
