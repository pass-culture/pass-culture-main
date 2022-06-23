import { createTheme } from '@mui/material/styles'
import React from 'react'
import {
  Link as RouterLink,
  LinkProps as RouterLinkProps,
} from 'react-router-dom'

import { Colors } from './Colors'

const LinkBehavior = React.forwardRef<
  HTMLAnchorElement,
  Omit<RouterLinkProps, 'to'> & { href: RouterLinkProps['to'] }
>((props, ref) => {
  const { href, ...other } = props
  // Map href (MUI) -> to (react-router)
  return <RouterLink data-testid="custom-link" ref={ref} to={href} {...other} />
})

export const theme = createTheme({
  palette: {
    primary: {
      // light: will be calculated from palette.primary.main,
      main: Colors.PRIMARY,
      dark: Colors.PRIMARY_DARK,
      // contrastText: will be calculated to contrast with palette.primary.main
    },
    info: {
      main: Colors.BLUE,
    },
    secondary: {
      main: Colors.SECONDARY,
    },
    success: {
      main: Colors.GREEN,
    },
    error: {
      main: Colors.RED,
    },
    warning: {
      main: Colors.YELLOW,
    },
    // Used by `getContrastText()` to maximize the contrast between
    // the background and the text.
    contrastThreshold: 3,
    // Used by the functions below to shift a color's luminance by approximately
    // two indexes within its tonal palette.
    // E.g., shift from Red 500 to Red 300 or Red 700.
    tonalOffset: 0.2,
  },
  components: {
    // MuiLink: {
    //   defaultProps: {
    //     component: LinkBehavior,
    //   } as LinkProps,
    // },
    MuiButtonBase: {
      defaultProps: {
        LinkComponent: LinkBehavior,
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          '&.MuiPaper-root': {
            color: Colors.WHITE,
          },
        },
        colorSecondary: {
          padding: 5,
          background: `linear-gradient(to right, ${Colors.PRIMARY}, ${Colors.SECONDARY});`,
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        docked: {
          width: 290,
        },
        paperAnchorDockedLeft: {
          width: 290,
        },
      },
    },
  },
})
