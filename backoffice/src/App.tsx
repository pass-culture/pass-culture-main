import CssBaseline from '@mui/material/CssBaseline'
import React, { createElement, useEffect } from 'react'
import { Admin, CustomRoutes, Resource } from 'react-admin'
import { Route, BrowserRouter } from 'react-router-dom'

import { CustomLayout } from './layout/CustomLayout'
import { theme } from './layout/theme'
import { eventMonitoring } from './libs/monitoring/sentry'
import { authProvider } from './providers/authProvider'
import { dataProvider } from './providers/dataProvider'
import { i18nProvider } from './providers/i18nProvider'
import { resources } from './resources'
import { LoginPage } from './resources/Login/LoginPage'
import { routes } from './routes'

export function App() {
  useEffect(() => {
    eventMonitoring.init({
      enabled: process.env.NODE_ENV !== 'development',
    })
  }, [])

  return (
    <>
      <BrowserRouter>
        <CssBaseline />
        <Admin
          dataProvider={dataProvider}
          authProvider={authProvider}
          i18nProvider={i18nProvider}
          layout={CustomLayout}
          theme={theme}
          loginPage={LoginPage}
        >
          {/* users */}
          {resources.map(resource => (
            <Resource
              key={resource.name}
              name={resource.name}
              list={resource.list}
              edit={resource.edit}
              create={resource.create}
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
