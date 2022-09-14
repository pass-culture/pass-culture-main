import AccountBoxIcon from '@mui/icons-material/AccountBox'
import ReviewsIcon from '@mui/icons-material/Reviews'
import { Divider } from '@mui/material'
import Box from '@mui/material/Box'
import * as React from 'react'
import { useState } from 'react'
import {
  MenuItemLink,
  MenuProps,
  usePermissions,
  useSidebarState,
  useTranslate,
} from 'react-admin'

import { searchPermission } from '../helpers/functions'
import { PermissionsEnum } from '../resources/PublicUsers/types'

import { SubMenu } from './SubMenu'

type MenuName = 'menuJeunes' | 'menuPros'

export const Menu = ({ dense = false }: MenuProps) => {
  const [state, setState] = useState({
    menuPros: false,
    menuJeunes: true,
  })
  const { permissions } = usePermissions()
  const formattedPermissions: PermissionsEnum[] = permissions
  const translate = useTranslate()
  const [open] = useSidebarState()

  const handleToggle = (menu: MenuName) => {
    setState(state => ({ ...state, [menu]: !state[menu] }))
  }

  return (
    <Box
      sx={{
        width: open ? 0 : 275,
        boxShadow: 3,
        mr: 1,
        marginTop: 1,
        paddingTop: 2,
        marginBottom: 0,
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
        icon={<AccountBoxIcon />}
      >
        <MenuItemLink
          to="/public_users/search"
          state={{ _scrollToTop: true }}
          primaryText={translate('menu.beneficiary', {
            smart_count: 2,
          })}
          dense={dense}
        />
        {/*<MenuItemLink*/}
        {/*  to="/users/list"*/}
        {/*  state={{ _scrollToTop: true }}*/}
        {/*  primaryText={translate('menu.users', {*/}
        {/*    smart_count: 2,*/}
        {/*  })}*/}
        {/*  dense={dense}*/}
        {/*  disabled*/}
        {/*/>*/}
        {/*<MenuItemLink*/}
        {/*  to="/users/features"*/}
        {/*  state={{ _scrollToTop: true }}*/}
        {/*  primaryText={translate('menu.features', {*/}
        {/*    smart_count: 2,*/}
        {/*  })}*/}
        {/*  dense={dense}*/}
        {/*  disabled*/}
        {/*/>*/}
        {/*<MenuItemLink*/}
        {/*  to="/users/categories"*/}
        {/*  state={{ _scrollToTop: true }}*/}
        {/*  primaryText={translate('menu.categories', {*/}
        {/*    smart_count: 2,*/}
        {/*  })}*/}
        {/*  dense={dense}*/}
        {/*  disabled*/}
        {/*/>*/}
      </SubMenu>
      <Divider />
      <SubMenu
        handleToggle={() => handleToggle('menuPros')}
        isOpen={state.menuPros}
        name="menu.prosTitle"
        dense={dense}
        icon={<AccountBoxIcon />}
      >
        <MenuItemLink
          to="/pro/search"
          state={{ _scrollToTop: true }}
          primaryText={translate('menu.pros', {
            smart_count: 2,
          })}
          dense={dense}
        />
      </SubMenu>
      {/*  <MenuItemLink*/}
      {/*    to="/pros/categories"*/}
      {/*    state={{ _scrollToTop: true }}*/}
      {/*    primaryText={translate('menu.categories', {*/}
      {/*      smart_count: 2,*/}
      {/*    })}*/}
      {/*    dense={dense}*/}
      {/*    disabled*/}
      {/*  />*/}
      {/*</SubMenu>*/}
      {/*<Divider />*/}
      {!!searchPermission(
        formattedPermissions,
        PermissionsEnum.managePermissions
      ) && (
        <MenuItemLink
          to="/roles"
          state={{ _scrollToTop: true }}
          primaryText={translate('menu.roleManagement', {
            smart_count: 2,
          })}
          leftIcon={<ReviewsIcon />}
          dense={dense}
        />
      )}
    </Box>
  )
}
