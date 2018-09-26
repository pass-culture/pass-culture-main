/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'
import ReactMarkdown from 'react-markdown'

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
    const backgroundImage = `url('${ROOT_PATH}/mosaic-k.png')`
    return (
      <div id="terms-page" className="page is-relative flex-rows">
        <PageHeader useClose theme="red" title="Mentions légales" />
        <main role="main" className="pc-main is-clipped">
          <div className="pc-scroll-container">
            <div className="padded content" style={{ backgroundImage }}>
              <ReactMarkdown source={source} />
              <div className="mt16">
                <p className="text-right">{`Pass Culture v.${appversion}`}</p>
              </div>
            </div>
          </div>
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
