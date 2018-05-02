import { createSelector } from 'reselect'

export default createSelector(
  state => state.data.offerers &&
    state.data.offerers[0] &&
    state.data.offerers[0].offererProviders,
  state => state.data.providers,
  (providers, offererProviders) =>
    providers.map(({ localClass, name }) => ({
      offererProviders:
        offererProviders &&
        offererProviders.filter(
          offererProvider =>
            offererProvider.provider.localClass === localClass
        ),
      name,
    }))
  )
