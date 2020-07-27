import PropTypes from 'prop-types'
import React from 'react'
import Helmet from 'react-helmet'

import {
  black as defaultColor,
  primary as primaryColor,
  tertiary as tertiaryColor,
} from '../../../styles/variables/index.scss'
import { isAppInFullscreen } from './domain/isAppInFullscreen'
import { shouldStatusBarBeColored } from './domain/shouldStatusBarBeColored'
import { shouldApplyTertiaryColor } from './domain/shouldApplyTertiaryColor'

export const StatusBarHelmet = ({ pathname }) => {
  const appIsInFullscreen = isAppInFullscreen()
  const statusBarIsColored = shouldStatusBarBeColored(pathname)
  const requiredIosMetaTag = (
    <meta
      content="black-translucent"
      name="apple-mobile-web-app-status-bar-style"
    />
  )
  const color = shouldApplyTertiaryColor(pathname) ? tertiaryColor : primaryColor
  const iosColoredStatusBar = <body style={`background-color:${statusBarIsColored ? color : defaultColor};`} />
  const androidColoredStatusBar = (
    <meta
      content={statusBarIsColored ? color : defaultColor}
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
