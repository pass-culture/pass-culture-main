import { createResponsiveStateReducer } from 'redux-responsive'

const browserConfig = { extraSmall: 425,
  small: 768,
  medium: 1024,
  large: 1440,
  extraLarge: 2560
}

const browser = createResponsiveStateReducer(browserConfig)

export default browser
