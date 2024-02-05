import React from 'react'
import { useRouteError } from 'react-router-dom'

import { isError } from 'apiClient/helpers'

export const ErrorBoundary = () => {
  const error = useRouteError()

  if (isError(error) && error.message.includes('dynamically imported module')) {
    // Reload page when a dynamic import fails (when we release a new version)
    // https://github.com/remix-run/react-router/discussions/10333
    // Error message is different in some browsers:
    // Chrome: Failed to fetch dynamically imported module
    // Firefox/Safari: error loading dynamically imported module)
    window.location.reload()

    return
  }

  return <div>Erreur !</div>
}
