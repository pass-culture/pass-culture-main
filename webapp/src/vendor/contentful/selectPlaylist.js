export const selectPlaylist = (entries, entryId) => {
  if (entries.length === 0) return

  // If no playlist is tagged, we show the last published homepage.
  const firstEntry = entries[0]

  // If we are coming from a deeplink, we suppose the entryId exists
  if (entryId) return entries.find(({ sys }) => sys.id === entryId) || firstEntry

  const masterPlaylists = entries.filter(entry =>
    'metadata' in entry ? entry.metadata.tags.map(({ sys }) => sys.id).includes('master') : false
  )

  return masterPlaylists.length ? masterPlaylists[0] : firstEntry
}
