module.exports = {
  moduleNameMapper: {
    '\\.(png|svg)': '<rootDir>/src/utils/svgrMock.js',
    '\\.(css|less|scss|sass)$': '<rootDir>/src/utils/styleMock.js',
  },
  modulePaths: ['node_modules', 'src'],
  setupFiles: ['<rootDir>/jest.setup.js', 'jest-canvas-mock'],
  testEnvironment: 'jest-environment-jsdom-sixteen',
  testMatch: [
    '<rootDir>/src/**/__tests__/**/*.{js,jsx,ts,tsx}',
    '<rootDir>/src/**/*.{spec,test}.{js,jsx,ts,tsx}',
  ],
  verbose: false,
}
