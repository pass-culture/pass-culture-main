import * as React from 'react';
import {useState} from 'react';
import Box from '@mui/material/Box';
import AccountBoxIcon from '@mui/icons-material/AccountBox';
import ApartmentIcon from '@mui/icons-material/Apartment';
import ReviewsIcon from '@mui/icons-material/Reviews';

import {
    useTranslate,
    DashboardMenuItem,
    MenuItemLink,
    MenuProps,
    useSidebarState,
} from 'react-admin';

import SubMenu from "./SubMenu";

type MenuName = 'menuJeunes' | 'menuPros';

const Menu = ({dense = false}: MenuProps) => {
    const [state, setState] = useState({
        menuPros: false,
        menuJeunes: true,
        menuCustomers: true,
    });
    const translate = useTranslate();
    const [open] = useSidebarState();

    const handleToggle = (menu: MenuName) => {
        setState(state => ({...state, [menu]: !state[menu]}));
    };

    return (
        <Box
            sx={{
                width: open ? 275 : 0,
                boxShadow: 5,
                mr: 2,
                marginTop: 2,
                paddingTop: 1,
                marginBottom: 1,
                transition: theme =>
                    theme.transitions.create('width', {
                        easing: theme.transitions.easing.sharp,
                        duration: theme.transitions.duration.leavingScreen,
                    }),
            }}
        >
            {/*<DashboardMenuItem/>*/}
            <SubMenu
                handleToggle={() => handleToggle('menuJeunes')}
                isOpen={state.menuJeunes}
                name="menu.usersTitle"
                dense={dense}
                icon={<AccountBoxIcon/>}>
                <MenuItemLink
                    to="/public_users/search"
                    state={{_scrollToTop: true}}
                    primaryText={translate(`menu.beneficiary`, {
                        smart_count: 2,
                    })}
                    dense={dense}
                />
                <MenuItemLink
                    to="/users/list"
                    state={{_scrollToTop: true}}
                    primaryText={translate(`menu.users`, {
                        smart_count: 2,
                    })}
                    dense={dense}
                />
                <MenuItemLink
                    to="/users/features"
                    state={{_scrollToTop: true}}
                    primaryText={translate(`menu.features`, {
                        smart_count: 2,
                    })}
                    dense={dense}
                />
                <MenuItemLink
                    to="/users/categories"
                    state={{_scrollToTop: true}}
                    primaryText={translate(`menu.categories`, {
                        smart_count: 2,
                    })}
                    dense={dense}
                />
            </SubMenu>

            <SubMenu
                handleToggle={() => handleToggle('menuPros')}
                isOpen={state.menuPros}
                name="menu.prosTitle"
                dense={dense}
                icon={<ApartmentIcon/>}
            >
                <MenuItemLink
                    to="/pros"
                    state={{_scrollToTop: true}}
                    primaryText={translate(`menu.pros`, {
                        smart_count: 2,
                    })}
                    dense={dense}
                />
                <MenuItemLink
                    to="/pros/categories"
                    state={{_scrollToTop: true}}
                    primaryText={translate(`menu.categories`, {
                        smart_count: 2,
                    })}
                    dense={dense}
                />
            </SubMenu>

            <MenuItemLink
                to="/reviews"
                state={{_scrollToTop: true}}
                primaryText={translate(`menu.roleManagement`, {
                    smart_count: 2,
                })}
                leftIcon={<ReviewsIcon/>}
                dense={dense}
            />
        </Box>
    );
};

export default Menu;