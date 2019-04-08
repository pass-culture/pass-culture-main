import withQueryRouter from 'with-query-router'

import { mapBrowserToApi } from '../../utils/translate'

export const CREATION = 'creation'

export const withFrenchQueryRouter = withQueryRouter({
  mapper: mapBrowserToApi,
})

export default withFrenchQueryRouter
