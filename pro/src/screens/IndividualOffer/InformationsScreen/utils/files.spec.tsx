import { imageFileToDataUrl } from './files'

describe('imageFileToDataUrl', () => {
  it('should succeed with a correct image file', async () => {
    // Crée un blob d'image correct (2x2 pixels violets)
    const imageBlob = new Blob(
      [
        'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAYAAABytg0kAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAATSURBVBhXY1jsueQ/CEMZS/4DAFlQCj3IYqsoAAAAAElFTkSuQmCC',
      ],
      { type: 'image/png' }
    )
    const imageFile = new File([imageBlob], 'test.png', { type: 'image/png' })

    const result = await imageFileToDataUrl(imageFile)

    expect(result).toContain('data:image/png;base64')
  })
})
