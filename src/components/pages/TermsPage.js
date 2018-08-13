import React from 'react'
import ReactMarkdown from 'react-markdown'

import { version } from '../../../package.json'

import Main from '../layout/Main'
import Footer from '../layout/Footer'
import { ROOT_PATH } from '../../utils/config'

const renderPageHeader = () => (
  <header>
    {'Mentions légales'}
  </header>
)

const renderPageFooter = () => {
  const footerProps = { borderTop: true, colored: true }
  return <Footer {...footerProps} />
}

class TermsPage extends React.PureComponent {
  constructor(props) {
    super(props)
    this.state = { mdText: '' }
  }

  async componentDidMount() {
    const result = await fetch(`${ROOT_PATH}/MentionsLegalesPass.md`)
    const mdText = await result.text()
    this.setState({ mdText })
  }

  render() {
    const { mdText } = this.state
    return (
      <Main
        backButton
        name="terms"
        header={renderPageHeader}
        footer={renderPageFooter}
      >
        <div className="content">
          <ReactMarkdown source={mdText} />
          <p className="version">
            <br />
            <br />
            {`Pass Culture version v${version}`}
          </p>
        </div>
      </Main>
    )
  }
}

export default TermsPage
