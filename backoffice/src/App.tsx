import * as React from 'react';
import {Admin, CustomRoutes, Resource} from 'react-admin'
import CssBaseline from '@mui/material/CssBaseline'
import {dataProvider} from './providers/dataProvider'
import authProvider from './providers/authProvider'
import {createBrowserHistory} from 'history'
import {i18nProvider} from './providers/i18nProvider'
import CustomLayout from "./layout/CustomLayout";
import CustomTheme from "./layout/Theme"
import UserSearch from "./resources/PublicUsers/UserSearch";
import UserDetail from "./resources/PublicUsers/UserDetail";
import LoginPage from "./resources/Login/LoginPage";
import {Route, BrowserRouter} from "react-router-dom";


function App() {
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
                    <Resource name="/public_users/search" list={UserSearch}/>
                    <CustomRoutes>
                        <Route path='/public_accounts/user/:id' element={<UserDetail/>}/>
                    </CustomRoutes>

                </Admin>
            </BrowserRouter>
        </>
    )
}

export default App
