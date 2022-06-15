import React, { createElement } from 'react'
import { Admin, CustomRoutes, Resource } from 'react-admin'
import CssBaseline from '@mui/material/CssBaseline'
import { dataProvider } from './providers/dataProvider'
import { authProvider } from './providers/authProvider'
import { i18nProvider } from './providers/i18nProvider'
import { CustomLayout } from './layout/CustomLayout'
import { CustomTheme } from './layout/Theme'
import { LoginPage } from './resources/Login/LoginPage'
import { Route, BrowserRouter } from 'react-router-dom'
import { resources } from './resources'
import { routes } from './routes'
import { init as SentryInit } from '@sentry/browser'
import { BrowserTracing } from '@sentry/tracing'
import { env } from './libs/environment/env'

SentryInit({
  dsn: 'https://examplePublicKey@o0.ingest.sentry.io/0',
  integrations: [new BrowserTracing()],
  environment: env.ENV,
  // We recommend adjusting this value in production, or using tracesSampler
  // for finer control
  tracesSampleRate: parseFloat(env.SAMPLE_RATE),
})

export function App() {
  return (
    <>
      <BrowserRouter>
        <CssBaseline />
        <Admin
          dataProvider={dataProvider}
          authProvider={authProvider}
          i18nProvider={i18nProvider}
          layout={CustomLayout}
          theme={CustomTheme}
          loginPage={LoginPage}
        >
          {/* users */}
          {resources.map(resource => (
            <Resource
              key={resource.name}
              name={resource.name}
              list={resource.list}
              edit={resource.edit}
            />
          ))}
          <CustomRoutes>
            {routes.map(route => (
              <Route
                key={route.path}
                path={route.path}
                element={createElement(route.component)}
              />
            ))}
          </CustomRoutes>
        </Admin>
      </BrowserRouter>
    </>
  )
}
