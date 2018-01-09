import classnames from 'classnames'
import React from 'react'
import { connect } from 'react-redux'

import Link from './Link'

import { closeNavigation,
  showNavigation
} from '../reducers/navigation'

const Hamburger = ({ className,
  closeNavigation,
  isActive,
  showNavigation
}) => {
  return (
    <div className={className || 'hamburger'}>
      <Link href='#footer'
        className={classnames({
          'hamburger__link--active': isActive
        }, 'hamburger__link')}
        onClick={e => {
          e.preventDefault()
          if (!isActive) {
            showNavigation()
          } else {
            // For keyboard users.
            // Not used for mouseclicks, instead we capture clicks via dismiss overlay
            closeNavigation()
          }
        }}
      >
        <div className='hamburger__link-box'>
          <div className='hamburger__link-inner' />
        </div>
      </Link>
    </div>
  )
}

export default connect(
  ({ navigation: { isActive } }) => ({ isActive }),
  { closeNavigation, showNavigation }
)(Hamburger)
