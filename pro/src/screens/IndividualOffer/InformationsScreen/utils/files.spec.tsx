import { imageFileToDataUrl } from './files'

describe('imageFileToDataUrl', () => {
  // Creates blob that represents a 2×2px violet square
  const imageBlob = new Blob(
    [
      'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAYAAABytg0kAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAATSURBVBhXY1jsueQ/CEMZS/4DAFlQCj3IYqsoAAAAAElFTkSuQmCC',
    ],
    { type: 'image/png' }
  )
  const imageFile = new File([imageBlob], 'test.png', { type: 'image/png' })

  it('should succeed with a correct image file', async () => {
    await expect(imageFileToDataUrl(imageFile)).resolves.toContain(
      'data:image/png;base64,'
    )
  })

  it('should should fail with an incorrect image file', async () => {
    vi.spyOn(FileReader.prototype, 'readAsDataURL').mockImplementation(() => {
      throw new Error('Not implemented')
    })
    await expect(imageFileToDataUrl(imageFile)).rejects.toThrowError()
  })
})
