import { withLogin } from 'pass-culture-shared'
import React, { Component } from 'react'

import Main from '../layout/Main'

class AccoutingPage extends Component {
  render() {
    return <Main name="accouting">VOTRE COMPTA</Main>
  }
}

export default withLogin({ failRedirect: '/connexion' })(AccoutingPage)
