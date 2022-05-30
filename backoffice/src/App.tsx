import * as React from 'react';
import {Admin, CustomRoutes, Resource} from 'react-admin'
import CssBaseline from '@mui/material/CssBaseline'
import {dataProvider} from './providers/dataProvider'
import authProvider from './providers/authProvider'
import {createBrowserHistory} from 'history'
import {i18nProvider} from './providers/i18nProvider'
import CustomLayout from "./layout/CustomLayout";
import CustomTheme from "./layout/Theme"
import UserSearch from "./resources/Components/UserSearch";
import UserDetail from "./resources/Components/UserDetail";
import LoginPage from "./resources/Components/LoginPage";
import {Route} from "react-router-dom";

const history = createBrowserHistory()


function App() {
    return (
        <>
            <CssBaseline/>
            <Admin
                history={history}
                dataProvider={dataProvider}
                authProvider={authProvider}
                i18nProvider={i18nProvider}
                layout={CustomLayout}
                theme={CustomTheme}
                loginPage={LoginPage}
            >
                {/* the bullishers */}
                {/*<Resource name="thebullishers/api/v1/signals" list={SignalList} create={SignalCreate} />*/}

                {/* users */}
                <Resource name="/public_users/search" list={UserSearch}/>
                <CustomRoutes>
                    <Route path='/public_accounts/user/:id' element={<UserDetail/>}/>
                </CustomRoutes>

            </Admin>
        </>
    )
}

export default App
