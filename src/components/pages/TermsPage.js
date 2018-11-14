/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'
import ReactMarkdown from 'react-markdown'

import { APP_VERSION, ROOT_PATH } from '../../utils/config'
import PageHeader from '../layout/PageHeader'
import NavigationFooter from '../layout/NavigationFooter'

const backgroundImage = `url('${ROOT_PATH}/mosaic-k.png')`
const mentionsLegalesFile = `${ROOT_PATH}/MentionsLegalesPass.md`

class TermsPage extends React.PureComponent {
  constructor(props) {
    super(props)
    this.state = { source: '' }
  }

  async componentDidMount() {
    const result = await fetch(mentionsLegalesFile)
    const source = await result.text()
    this.setState({ source })
  }

  render() {
    const { source } = this.state
    const { appversion } = this.props
    return (
      <div id="terms-page" className="page is-relative flex-rows">
        <PageHeader useClose theme="red" title="Mentions légales" />
        <main role="main" className="pc-main is-clipped">
          <div className="pc-scroll-container">
            <div className="padded content" style={{ backgroundImage }}>
              <ReactMarkdown source={source} />
              <div className="mt16">
                <p id="terms-page-appversion" className="text-right">
                  {`Pass Culture v.${appversion}`}
                </p>
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
  // NOTE -> `appversion`
  // est passé dans les props pour les tests jests/enzyme
  appversion: PropTypes.string,
}

export default TermsPage
