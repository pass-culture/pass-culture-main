import { createTheme } from '@mui/material/styles'

import { colors } from './Colors'

export const theme = createTheme({
  palette: {
    primary: {
      // light: will be calculated from palette.primary.main,
      main: colors.PRIMARY,
      dark: colors.PRIMARY_DARK,
      // contrastText: will be calculated to contrast with palette.primary.main
    },
    secondary: {
      main: colors.SECONDARY,
    },
    success: {
      main: colors.GREEN,
    },
    error: {
      main: colors.RED,
    },
    warning: {
      main: colors.YELLOW,
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
    MuiAppBar: {
      styleOverrides: {
        root: {
          '&.MuiPaper-root': {
            color: colors.WHITE,
          },
        },
        colorSecondary: {
          padding: 5,
          background: `linear-gradient(to right, ${colors.PRIMARY}, ${colors.SECONDARY});`,
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
