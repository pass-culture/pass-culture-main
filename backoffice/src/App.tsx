import React, { createElement } from 'react';
import {Admin, CustomRoutes, Resource} from 'react-admin'
import CssBaseline from '@mui/material/CssBaseline'
import {dataProvider} from './providers/dataProvider'
import {authProvider} from './providers/authProvider'
import {i18nProvider} from './providers/i18nProvider'
import CustomLayout from "./layout/CustomLayout";
import CustomTheme from "./layout/Theme"
import LoginPage from "./resources/Login/LoginPage";
import {Route, BrowserRouter} from "react-router-dom";
import { resources } from './resources'
import { routes } from './routes'

export function App() {
    return (
        <>
            <BrowserRouter>
                <CssBaseline/>
                <Admin
                    dataProvider={dataProvider}
                    authProvider={authProvider}
                    i18nProvider={i18nProvider}
                    layout={CustomLayout}
                    theme={CustomTheme}
                    loginPage={LoginPage}
                >

                    {/* users */}
                    {resources.map((resource) => <Resource key={resource.name} name={resource.name} list={resource.list} edit={resource.edit} />)}
                    <CustomRoutes>
                        {routes.map((route) => <Route key={route.path} element={createElement(route.component)}/>)}
                    </CustomRoutes>
                </Admin>
            </BrowserRouter>
        </>
    )
}
