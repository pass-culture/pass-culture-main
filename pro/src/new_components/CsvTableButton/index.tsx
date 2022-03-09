import React, { FunctionComponent } from 'react'
import { withRouter } from 'react-router-dom'
import type { RouteComponentProps } from 'react-router-dom'

export interface CsvTableButtonProps extends RouteComponentProps {
  children?: string
  isDisabled?: boolean
  href: string
  url?: string
}

const CsvTableButton: FunctionComponent<CsvTableButtonProps> = ({
  history,
  href,
  location,
  url,
  children = '',
  isDisabled = false,
}) => {
  const handleRedirectToUrl = () => {
    const { pathname } = location
    const nextUrl = url ? url : pathname + '/detail'
    history.push(nextUrl, href)
  }

  return (
    <button
      className="secondary-button"
      disabled={isDisabled}
      onClick={handleRedirectToUrl}
      type="button"
    >
      {children}
    </button>
  )
}
export { CsvTableButton }
export default withRouter(CsvTableButton)
