import withQueryRouter from 'with-query-router'

export const CREATION = 'creation'
export const MODIFICATION = 'modification'

export const mapBrowserToApi = {
  'mots-cles': 'keywords',
  reservations: 'bookings',
}

const withFrenchQueryRouter = withQueryRouter({
  mapper: mapBrowserToApi,
})

export default withFrenchQueryRouter
