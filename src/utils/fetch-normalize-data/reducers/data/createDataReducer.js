import getNormalizedCommittedState from '../../normalize/getNormalizedCommittedState'
import getNormalizedDeletedState from '../../normalize/getNormalizedDeletedState'
import getNormalizedMergedState from '../../normalize/getNormalizedMergedState'
import { getDefaultCommitFrom } from '../../normalize/utils'
import {
  ASSIGN_DATA,
  COMMIT_DATA,
  DELETE_DATA,
  MERGE_DATA,
  REINITIALIZE_DATA
} from './actions'
import getDeletedPatchByActivityTag from './getDeletedPatchByActivityTag'
import getSuccessState from './getSuccessState'
import reinitializeState from './reinitializeState'


export const createDataReducer = (initialState = {}, extraConfig = {}) => {
  const wrappedReducer = (state, action) => {
    const keepFromCommit =
      (action.config || {}).keepFromCommit ||
      extraConfig.keepFromCommit ||
      getDefaultCommitFrom

    if (action.type === ASSIGN_DATA) {
      return {
        ...state,
        ...action.patch,
      }
    }

    if (action.type === COMMIT_DATA) {
      const { commits: nextCommits } = getNormalizedMergedState(
        state,
        { commits: action.commits },
        {
          getDatumIdKey: () => 'localIdentifier',
          getDatumIdValue: commit =>
            commit.id || `${commit.uuid}/${commit.dateCreated}`,
          isMergingDatum: true,
        }
      )
      return getNormalizedCommittedState(
        state,
        { commits: nextCommits },
        { keepFromCommit }
      )
    }

    if (action.type === DELETE_DATA) {
      let patch = action.patch || state
      if (action.config.activityTags) {
        patch = getDeletedPatchByActivityTag(patch, action.config.activityTags)
      }
      return {
        ...state,
        ...getNormalizedDeletedState(state, patch, action.config),
      }
    }

    if (action.type === MERGE_DATA) {
      return {
        ...state,
        ...getNormalizedMergedState(state, action.patch, action.config),
      }
    }

    if (action.type === REINITIALIZE_DATA) {
      return reinitializeState(state, initialState, action.config)
    }

    if (
      action.type === 'persist/REHYDRATE' &&
      typeof action.payload !== 'undefined' &&
      typeof action.payload.commits !== 'undefined'
    ) {
      return getNormalizedCommittedState(state, action.payload, {
        keepFromCommit,
      })
    }

    if (/SUCCESS_DATA_(DELETE|GET|POST|PUT|PATCH)_(.*)/.test(action.type)) {
      return {
        ...state,
        ...getSuccessState(state, action),
      }
    }

    return state
  }

  const reducer = (state = initialState, action) => {
    const keepFromCommit =
      (action.config || {}).keepFromCommit ||
      extraConfig.keepFromCommit ||
      getDefaultCommitFrom

    const nextState = wrappedReducer(state, action)
    if (state.commits !== nextState.commits) {
      return getNormalizedCommittedState(
        nextState,
        { commits: nextState.commits },
        { keepFromCommit }
      )
    }
    return nextState
  }

  return reducer
}

export default createDataReducer
