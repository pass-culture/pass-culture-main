import { getImageDimensions } from './getImageDimensions'

describe('getImageDimensions', () => {
  const createObjectURLMock = vi.spyOn(URL, 'createObjectURL')
  const revokeObjectURLMock = vi.spyOn(URL, 'revokeObjectURL')
  const mockFile = { name: 'test-image.png', width: 1920, height: 1080 } as any

  beforeEach(() => {
    createObjectURLMock.mockImplementation((file) => file as unknown as string)
    revokeObjectURLMock.mockImplementation(() => {})
    vi.stubGlobal('URL', {
      ...globalThis.URL,
      createObjectURL: createObjectURLMock,
      revokeObjectURL: revokeObjectURLMock,
    })
    vi.stubGlobal(
      'Image',
      class {
        onload: () => void = () => {}
        onerror: () => void = () => {}
        width: number = 0
        height: number = 0

        set src(file: any) {
          if (file) {
            this.width = file.width || 0
            this.height = file.height || 0

            setTimeout(() => {
              this.onload()
            }, 5)
          } else {
            setTimeout(() => {
              this.onerror()
            }, 5)
          }
        }
      }
    )
  })

  afterAll(() => {
    vi.unstubAllGlobals()
  })

  it('should return image dimensions', async () => {
    const result = await getImageDimensions(mockFile)

    expect(result).toEqual({ width: 1920, height: 1080 })
    expect(createObjectURLMock).toHaveBeenCalledWith(mockFile)
  })

  it('should revoke url', async () => {
    await getImageDimensions(mockFile)

    expect(revokeObjectURLMock).toHaveBeenCalledTimes(1)
  })

  it('should revoke url on failure', async () => {
    const promise = getImageDimensions(null as any)

    await expect(promise).rejects.toThrow("Impossible de lire l'image")
    expect(revokeObjectURLMock).toHaveBeenCalledTimes(1)
  })
})
