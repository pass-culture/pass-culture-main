import { createSelector } from 'reselect'

const emptyManagedOccasions = []

export default (selectManagedVenues) => createSelector(
  selectManagedVenues,
  venues => emptyManagedOccasions
)
