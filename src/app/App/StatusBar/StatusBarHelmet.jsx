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
  const statusBarShouldBeColored = shouldStatusBarBeColored(pathname)
  const requirediOSMetaTag = (
    <meta
      content="black-translucent"
      name="apple-mobile-web-app-status-bar-style"
    />
  )
  const iOSColoredStatusBar = statusBarShouldBeColored ? (
    <body style={`background-color:${primaryColor};`} />
  ) : (
    <body style={`background-color:${defaultColor};`} />
  )
  const androidColoredStatusBar = statusBarShouldBeColored ? (
    <meta
      content={primaryColor}
      name="theme-color"
    />
  ) : (
    <meta
      content={defaultColor}
      name="theme-color"
    />
  )

  return (
    <Helmet>
      {requirediOSMetaTag}
      {appIsInFullscreen && iOSColoredStatusBar}
      {appIsInFullscreen && androidColoredStatusBar}
    </Helmet>
  )
}

StatusBarHelmet.propTypes = { pathname: PropTypes.string.isRequired }
