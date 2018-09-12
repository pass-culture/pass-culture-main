/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import ReactMarkdown from 'react-markdown'
import { Scrollbars } from 'react-custom-scrollbars'

import { ROOT_PATH, APP_VERSION } from '../../utils/config'
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
    const backgroundImage = `url('${ROOT_PATH}/mosaic-k@2x.png')`
    return (
      <div id="terms-page" className="page flex-rows">
        <header className="pc-header pc-theme-red is-relative">
          <h1>
            <span>Mentions légales</span>
          </h1>
        </header>
        <main role="main" className="pc-main">
          <Scrollbars>
            <div className="padded content" style={{ backgroundImage }}>
              <ReactMarkdown source={source} />
              <div className="mt16">
                <p>Pass Culture version v{APP_VERSION}</p>
              </div>
            </div>
          </Scrollbars>
        </main>
        <NavigationFooter theme="white" />
      </div>
    )
  }
}

export default TermsPage
