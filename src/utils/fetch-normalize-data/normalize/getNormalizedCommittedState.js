import uniq from 'lodash.uniq'
import getNormalizedMergedState from './getNormalizedMergedState'
import { getDefaultCommitFrom } from './utils'

export function getNormalizedCommittedState(state, patch, config) {
  const keepFromCommit = config.keepFromCommit || getDefaultCommitFrom

  const stateWithPossibleDeletedCollections = { ...state }
  const { commits } = patch

  const deletedCommitUuids = (commits || [])
    .filter(commit => commit.isRemoved)
    .map(commit => commit.uuid)

  const notSoftDeletedCommits = (commits || []).filter(
    commit => !deletedCommitUuids.includes(commit.uuid)
  )

  const sortedCommits = notSoftDeletedCommits.sort((commit1, commit2) =>
    new Date(commit1.dateCreated) < new Date(commit2.dateCreated) ? -1 : 1
  )

  const firstDateCreatedsByUuid = {}
  sortedCommits.forEach(commit => {
    if (!firstDateCreatedsByUuid[commit.uuid]) {
      firstDateCreatedsByUuid[commit.uuid] = commit.dateCreated
    }
  })

  const collectionNames = uniq(
    (commits || []).map(commit => commit.collectionName)
  )
  collectionNames.forEach(collectionName => {
    delete stateWithPossibleDeletedCollections[collectionName]
  })

  return sortedCommits.reduce(
    (aggregation, commit) => ({
      ...aggregation,
      ...getNormalizedMergedState(
        aggregation,
        {
          [commit.collectionName]: [
            {
              firstDateCreated: firstDateCreatedsByUuid[commit.uuid],
              lastDateCreated: commit.dateCreated,
              uuid: commit.uuid,
              ...commit.patch,
              ...keepFromCommit(commit),
            },
          ],
        },
        {
          getDatumIdKey: () => 'uuid',
          getDatumIdValue: commit => commit.uuid,
          isMergingDatum: true,
        }
      ),
    }),
    { ...stateWithPossibleDeletedCollections, ...patch }
  )
}

export default getNormalizedCommittedState
