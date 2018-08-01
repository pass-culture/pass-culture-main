import React, { Component } from 'react'
import ReactMarkdown from 'react-markdown'

import Main from '../layout/Main'
import { ROOT_PATH } from '../../utils/config'

class TermsPage extends Component {
  constructor() {
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
      <Main
        name="terms"
        footer={{ borderTop: true, colored: true }}
        backButton>
        <header>Mentions légales</header>
        <div className="content">
          <ReactMarkdown source={mdText} />
          <p className="version">
            <br />
            <br />
            Pass Culture version ##VERSION##
          </p>
        </div>
      </Main>
    )
  }
}

export default TermsPage
