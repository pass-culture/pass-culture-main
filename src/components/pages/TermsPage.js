import React, { Component } from 'react'
import ReactMarkdown from 'react-markdown'

import PageWrapper from '../layout/PageWrapper'
import { ROOT_PATH } from '../../utils/config'

class TermsPage extends Component {
  constructor () {
      super()
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
      <PageWrapper
        name="terms"
        menuButton={{ borderTop: true, colored: true }}
        backButton
      >
        <header>Mentions légales</header>
        <div className="content">
          <ReactMarkdown source={mdText} />
        </div>
      </PageWrapper>
    )
  }
}

export default TermsPage
