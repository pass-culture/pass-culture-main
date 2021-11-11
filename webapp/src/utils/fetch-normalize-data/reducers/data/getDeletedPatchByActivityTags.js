export const getDeletedPatchByActivityTags = (patch, activityTags) => {
  const deletedPatch = {}
  Object.keys(patch).forEach(key => {
    const filteredEntities = patch[key].filter(
      entity =>
        entity.__ACTIVITIES__ &&
        entity.__ACTIVITIES__.length > 0 &&
        entity.__ACTIVITIES__.every(activityTag =>
          activityTags.includes(activityTag)
        )
    )
    deletedPatch[key] = filteredEntities
  })
  return deletedPatch
}
