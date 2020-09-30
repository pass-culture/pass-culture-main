import moment from 'moment'
import createCachedSelector from 're-reselect'

export const selectMediationById = createCachedSelector(
  state => state.data.mediations,
  (state, mediationId) => mediationId,
  (mediations, mediationId) => mediations.find(m => m.id === mediationId)
)((state, mediationId = '') => mediationId)

export const selectMediationsByOfferId = createCachedSelector(
  state => state.data.mediations,
  (state, offerId) => offerId,
  (mediations, offerId) => {
    let selectedMediations = mediations

    // optional offerId
    if (offerId) selectedMediations = mediations.filter(m => m.offerId === offerId)

    // sort by creation date
    selectedMediations &&
      selectedMediations.sort((m1, m2) => moment(m1.dateCreated) - moment(m2.dateCreated))

    return selectedMediations
  }
)((state, offerId = '') => offerId)
