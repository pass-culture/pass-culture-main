import { selectPlaylist } from '../selectPlaylist'

const masterTag = { sys: { id: 'master', linkType: 'Tag', type: 'Link' } }

const entryId = 'entryId'

const defaultEntry = {
  metadata: { tags: [] },
  sys: {
    id: '16PgpnlCOYYIhUTclR0oO4',
    contentType: { sys: { type: 'Link', linkType: 'ContentType', id: 'homepage' } },
  },
  fields: { modules: [] },
}

const entryWithId = { ...defaultEntry, sys: { ...defaultEntry.sys, id: entryId } }
const entryMaster = { ...defaultEntry, metadata: { tags: [masterTag] } }

const allPlaylists = [entryMaster, defaultEntry, entryWithId]

describe('selectPlaylist', () => {
  it('should retrieve the playlist with the entryId', () => {
    const playlist = selectPlaylist(allPlaylists, entryId)
    expect(playlist).toStrictEqual(entryWithId)
  })

  it('should retrieve the playlist tagged master if available', () => {
    const playlist = selectPlaylist(allPlaylists, null)
    expect(playlist).toStrictEqual(entryMaster)
  })

  it('should retrieve the first playlist if no playlist tagged master', () => {
    const playlist = selectPlaylist([defaultEntry, entryWithId], null)
    expect(playlist).toStrictEqual(defaultEntry)
  })
})
