// react hooks and usages doc : https://reactjs.org/docs/hooks-intro.html
import type { Location } from 'history'
import React from 'react'
import { useLocation, Redirect } from 'react-router-dom'

const RedirectLogin = (): JSX.Element => {
  const location: Location = useLocation()
  return <Redirect to={`/connexion${location.search}`} />
}

export default RedirectLogin
