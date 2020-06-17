import PropTypes from 'prop-types'
import React from 'react'
import Helmet from 'react-helmet'

import {
  black as defaultColor,
  primary as primaryColor,
} from '../../../styles/variables/index.scss'
import { isAppInFullscreen } from './domain/isAppInFullscreen'
import { shouldStatusBarBeColored } from './domain/shouldStatusBarBeColored'

export const StatusBarHelmet = ({ pathname }) => {
  const appIsInFullscreen = isAppInFullscreen()
  const statusBarIsColored = shouldStatusBarBeColored(pathname)
  const requiredIosMetaTag = (
    <meta
      content="black-translucent"
      name="apple-mobile-web-app-status-bar-style"
    />
  )
  const iosColoredStatusBar = <body style={`background-color:${statusBarIsColored ? primaryColor : defaultColor};`} />
  const androidColoredStatusBar = (
    <meta
      content={statusBarIsColored ? primaryColor : defaultColor}
      name="theme-color"
    />
  )

  return (
    <Helmet>
      {requiredIosMetaTag}
      {appIsInFullscreen && iosColoredStatusBar}
      {appIsInFullscreen && androidColoredStatusBar}
    </Helmet>
  )
}

StatusBarHelmet.propTypes = { pathname: PropTypes.string.isRequired }
