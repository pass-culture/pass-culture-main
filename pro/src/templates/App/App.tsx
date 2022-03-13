import cn from 'classnames'
import React from 'react'

import style from './App.module.scss'
import { AppHeader } from './AppHeader'
import { AppContentCenter } from './AppContentCenter'
import { AppContentFullScreen } from './AppContentFullScreen'

interface IAppProps {
  children: React.ReactNode | React.ReactNode[]
  className?: string
  small?: boolean
}

const App = ({ children, className, small }: IAppProps): JSX.Element => (
  <div className={cn(style['app-tempalte'], className)}>{children}</div>
)

App.Header = AppHeader
App.Content = AppContentCenter

export default App
