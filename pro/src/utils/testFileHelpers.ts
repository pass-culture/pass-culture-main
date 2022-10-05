export interface ICreateImageArgs {
  name?: string
  type?: string
  sizeInMB?: number
}
export const createFile = ({
  name = 'example.json',
  type = 'application/json',
  sizeInMB = 1,
}: ICreateImageArgs = {}): File => {
  const oneMB = 1024 * 1024
  const file = new File([''], name, { type })
  Object.defineProperty(file, 'size', { value: oneMB * sizeInMB })
  return file
}

export interface ICreateImageFileArgs {
  name?: string
  type?: string
  sizeInMB?: number
  width?: number
  height?: number
}
export const createImageFile = ({
  name = 'example.png',
  type = 'image/png',
  sizeInMB = 1,
  width = 100,
  height = 100,
}: ICreateImageFileArgs = {}): File => {
  const file = createFile({ name, type, sizeInMB })
  Object.defineProperty(file, 'width', {
    value: width,
    configurable: true,
  })
  Object.defineProperty(file, 'height', {
    value: height,
    configurable: true,
  })
  jest
    .spyOn(global, 'createImageBitmap')
    .mockResolvedValue({ width, height } as ImageBitmap)
  return file
}
