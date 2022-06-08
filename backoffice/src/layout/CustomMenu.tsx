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
    });

    const translate = useTranslate();
    const [open] = useSidebarState();

    const handleToggle = (menu: MenuName) => {
        setState(state => ({...state, [menu]: !state[menu]}));
    };

    return (
        <Box
            sx={{
                width: open ? 0 : 275,
                boxShadow: 3,
                mr: 1,
                marginTop: 1,
                paddingTop: 2,
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
                    disabled
                />
                <MenuItemLink
                    to="/users/features"
                    state={{_scrollToTop: true}}
                    primaryText={translate(`menu.features`, {
                        smart_count: 2,
                    })}
                    dense={dense}
                    disabled
                />
                <MenuItemLink
                    to="/users/categories"
                    state={{_scrollToTop: true}}
                    primaryText={translate(`menu.categories`, {
                        smart_count: 2,
                    })}
                    dense={dense}
                    disabled
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
                    disabled
                />
                <MenuItemLink
                    to="/pros/categories"
                    state={{_scrollToTop: true}}
                    primaryText={translate(`menu.categories`, {
                        smart_count: 2,
                    })}
                    dense={dense}
                    disabled
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
                disabled
            />
        </Box>
    );
};

export default Menu;