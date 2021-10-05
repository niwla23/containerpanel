import { createNameFromDescription} from '@/helpers'

describe('createNameFromDescription', () => {
  test('repalce umlaute', () => {
    expect(createNameFromDescription("täst")).toBe("taest")
  })
  test('replaces spaces with undescores', () => {
    expect(createNameFromDescription("this is a test")).toBe("this_is_a_test")
  })
  test('replaces uppercase letters to lowercase', () => {
    expect(createNameFromDescription("Hello this is A test")).toBe("hello_this_is_a_test")
  })
  test('trims string', () => {
    expect(createNameFromDescription(" this is a test ")).toBe("this_is_a_test")
  })
  test('text with space and number', () => {
    expect(createNameFromDescription("Testserver 444")).toBe("testserver_444")
  })
  test('text with space and number and special characters', () => {
    expect(createNameFromDescription("Niwla23's Testing server #4__")).toBe("niwla23_s_testing_server_4")
  })
  test('This is a test servä 33_', () => {
    expect(createNameFromDescription("This is a test servä 33_")).toBe("this_is_a_test_servae_33")
  })
})
