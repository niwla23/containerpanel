import { bytesToString } from '@/helpers'

describe('bytesToString', () => {
  test('displays as Gigabytes if equal 1 GB', () => {
    expect(bytesToString(1000000000)).toBe("1.00 GB")
  })
  test('displays as Gigabytes if bigger than 1 GB', () => {
    expect(bytesToString(2500000000)).toBe("2.50 GB")
  })
  test('displays as Megabytes if equal to 1 MB', () => {
    expect(bytesToString(1000000)).toBe("1.00 MB")
  })
  test('displays as Megabytes if bigger than 1 MB', () => {
    expect(bytesToString(3400000)).toBe("3.40 MB")
  })
})
