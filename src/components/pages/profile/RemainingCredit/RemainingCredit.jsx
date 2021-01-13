import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'

import User from '../ValueObjects/User'
import DepositVersion1 from './DepositVersion1'
import DepositVersion2 from './DepositVersion2'

class RemainingCredit extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      isReadMoreVisible: false,
    }
  }

  handleToggleReadMore = () => {
    this.setState(previousState => ({ isReadMoreVisible: !previousState.isReadMoreVisible }))
  }

  render() {
    const { user } = this.props

    if (user.deposit_version === 1) {
      return <DepositVersion1 user={user} />
    } else {
      return <DepositVersion2 user={user} />
    }
  }
}

RemainingCredit.propTypes = {
  user: PropTypes.shape(User).isRequired,
}

export default RemainingCredit
