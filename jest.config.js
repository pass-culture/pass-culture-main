module.exports = {
  collectCoverageFrom: [
    '**/*.{js,jsx}',
    '!**/*Mock.jsx',
    '!reselect.js',
    '!jest.setup.js',
    '!.jest-polyfill.js',
    // "!**/node_modules/**",
  ],
  moduleFileExtensions: [
    'web.js',
    'mjs',
    'js',
    'json',
    'web.jsx',
    'jsx',
    'node',
  ],
  moduleNameMapper: {
    '^react-native$': 'react-native-web',
  },
  modulePaths: ['node_modules', 'src'],
  setupFiles: ['<rootDir>/.jest-polyfill.js', '<rootDir>/jest.setup.js'],
  testEnvironment: 'node',
  testMatch: [
    '<rootDir>/src/**/__tests__/**/*.{js,jsx,mjs}',
    '<rootDir>/src/**/?(*.)(spec|test).{js,jsx,mjs}',
    '**/?(*.)+(spec).js?(x)',
  ],
  testPathIgnorePatterns: ['<rootDir>/.next/', '<rootDir>/node_modules/'],
  testURL: 'http://localhost',
  transform: {
    '^.+\\.js$': 'babel-jest',
    '^.+\\.(js|jsx|mjs)$': '<rootDir>/node_modules/babel-jest',
    '^.+\\.css$': '<rootDir>/config/jest/cssTransform.js',
    '^(?!.*\\.(js|jsx|mjs|css|json)$)':
      '<rootDir>/config/jest/fileTransform.js',
  },
  transformIgnorePatterns: [
    '<rootDir>/node_modules/',
    '[/\\\\]node_modules[/\\\\].+\\.(js|jsx|mjs)$',
  ],
  verbose: true,
}
