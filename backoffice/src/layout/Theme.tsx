import { createTheme } from '@mui/material/styles';

const CustomTheme = createTheme({
    palette: {
        primary: {
            // light: will be calculated from palette.primary.main,
            main: '#eb0055',
            dark: '#c10046'
            // contrastText: will be calculated to contrast with palette.primary.main
        },
        secondary: {
            main: '#320096',
        },
        success : {
            main : '#15884f'
        },
        error : {
            main : '#e60039'
        },
        warning : {
            main : '#ffea00'
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
        MuiAppBar : {
            styleOverrides : {
                root: {
                    "&.MuiPaper-root":{
                        color: "white",
                    },
                },
                colorSecondary : {
                    padding: 5,
                    background : "linear-gradient(to right, #eb0055, #320096);",
                },

            }
        },
        MuiDrawer : {
            styleOverrides : {
                docked: {
                    width: 290,
                },
                paperAnchorDockedLeft : {
                    width: 290
                }
            }
        },
    },
});

export default CustomTheme;