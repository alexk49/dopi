import { afterEach, beforeEach, describe, expect, jest, it, test } from '@jest/globals';
import { buildCompletedFilesList, countLines, fetchFormResponse, fetchServerData, fetchCompleteFiles, fetchQueueCount, getCookie, handleFormErrors, showMessage, toggleElVisibility, updateQueueCounter } from '../static/utils.js';

describe('buildCompletedFilesList', () => {
  test('returns a UL element with links for each filename', () => {
    const filenames = ['file1.txt', 'file2.txt'];
    const ul = buildCompletedFilesList(filenames);

    expect(ul).toBeInstanceOf(HTMLUListElement);
    expect(ul.children.length).toBe(2);
    expect(ul.children[0].textContent).toBe('file1.txt');
    expect(ul.children[1].textContent).toBe('file2.txt');
  });
});

describe('UpdateQueueCounter', () => {
  test('Test queue counter updates with given value', () => {
    let queueCounterEl = document.createElement('div');

    updateQueueCounter(queueCounterEl, "1")

    expect(queueCounterEl.textContent).toBe('There is 1 file in the queue to be processed.');

    updateQueueCounter(queueCounterEl, "3")

    expect(queueCounterEl.textContent).toBe('There are 3 files in the queue to be processed.');
  });
});

describe('getCookie', () => {
  beforeEach(() => {
    Object.defineProperty(document, 'cookie', {
      writable: true,
      value: 'csrf_token=test-token; session_id=abc123',
      configurable: true,
    });
  });

  it('returns the value of an existing cookie', () => {
    expect(getCookie('csrf_token')).toBe('test-token');
    expect(getCookie('session_id')).toBe('abc123');
  });

  it('returns null for a missing cookie', () => {
    expect(getCookie('nonexistent')).toBe(null);
  });
});


describe('toggleElVisibility', () => {
  let el;

  beforeEach(() => {
    el = document.createElement('div');
    el.hidden = true;
  });

  it("should show element and run callback", async () => {
    const mockCallBack = jest.fn();

    toggleElVisibility(el, mockCallBack);

    expect(el.hidden).toBe(false);
    expect(mockCallBack).toHaveBeenCalled();
  });

  it("should hide element and not run callback", async () => {
    const mockCallBack = jest.fn();
    el.hidden = false;

    toggleElVisibility(el, mockCallBack);

    expect(el.hidden).toBe(true);
    expect(mockCallBack).not.toHaveBeenCalled();
  })

  it("should work with no callback", async () => {
    toggleElVisibility(el)

    expect(el.hidden).toBe(false)
  })
});

describe('countLines', () => {
  it("shows correct message for 2 lines", () => {
    const textarea = document.createElement("textarea");
    const counter = document.createElement("div");

    textarea.value = "10.1000/1\n10.1000/2";

    countLines(counter, textarea);

    expect(counter.textContent).toBe("2 Dois added");
  });
});


describe('fetchServerData', () => {
  beforeEach(() => {
    globalThis.fetch = jest.fn();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  test("returns parsed JSON data when response is OK", async () => {
    const mockData = { message: "Success" };

    fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockData),
    });

    const result = await fetchServerData("/test-url");
    expect(result).toEqual(mockData);
    expect(fetch).toHaveBeenCalledWith("/test-url");
  });

  test("returns empty object and logs error on fetch failure", async () => {
    fetch.mockRejectedValueOnce(new Error("Network error"));

    const result = await fetchServerData("/fail-url");
    expect(result).toEqual({ 'success': 'false', 'message': "Error fetching data from: /fail-url, Error: Network error" }
    );
  });

  test("throws on non-ok response and returns empty object", async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: () => Promise.resolve({ error: "Server error" }),
    });

    const result = await fetchServerData("/error-url");
    expect(result.message).toEqual("Error fetching data from: /error-url, Error: HTTP error: 500");
  });
});

describe('fetchQueueCount', () => {
  globalThis.fetch = jest.fn();
  test("Returns queue count when json is correct", async () => {
    const mockData = { queue_count: "2" };

    fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockData),
    });

    const result = await fetchQueueCount();
    expect(result).toEqual("2");
    expect(fetch).toHaveBeenCalled();
  });
});


describe('fetchCompleteFiles', () => {
  globalThis.fetch = jest.fn();
  test("Returns complete files list when json is correct", async () => {
    const mockData = { completed: ["file1.csv", "file2.csv", "file3.csv"] };

    fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockData),
    });

    const result = await fetchCompleteFiles();
    expect(result).toEqual(mockData.completed);
    expect(fetch).toHaveBeenCalled();
  });
});


describe('fetchFormResponse', () => {
  globalThis.fetch = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('should successfully fetch data and return json response', async () => {
    const url = '/submit';
    const formData = new FormData();
    formData.append('name', 'Test User');
    formData.append('email', 'test@example.com');

    const mockResponse = {
      json: jest.fn().mockResolvedValue({ success: true, message: 'Success' }),
      ok: true,
      status: 200
    };
    fetch.mockResolvedValue(mockResponse);

    const result = await fetchFormResponse(url, formData);

    expect(fetch).toHaveBeenCalledWith(url, {
      method: 'POST',
      body: formData
    });

    expect(mockResponse.json).toHaveBeenCalled();

    expect(result).toEqual({ success: true, message: 'Success' });
  });

  test('should handle network errors', async () => {
    const url = '/submit';
    const formData = new FormData();

    const networkError = new Error('Network failure');
    fetch.mockRejectedValue(networkError);

    const result = await fetchFormResponse(url, formData);

    expect(fetch).toHaveBeenCalledWith(url, {
      method: 'POST',
      body: formData
    });

    expect(result.message).toEqual('Error posting form data to: /submit - Error: Network failure');
  });
});


describe('showMessage', () => {
  let messageDiv;

  beforeEach(() => {
    messageDiv = document.createElement('div');
  });

  test('displays success message correctly', () => {
    showMessage(messageDiv, 'Success!', true);

    expect(messageDiv.textContent).toBe('Success!');
    expect(messageDiv.style.color).toBe('green');
    expect(messageDiv.hasAttribute('role')).toBe(false);
    expect(messageDiv.hasAttribute('aria-live')).toBe(false);
  });

  test('displays error message with alert attributes', () => {
    showMessage(messageDiv, 'Failed!', false);

    expect(messageDiv.textContent).toBe('Failed!');
    expect(messageDiv.style.color).toBe('red');
    expect(messageDiv.getAttribute('role')).toBe('alert');
    expect(messageDiv.getAttribute('aria-live')).toBe('assertive');
  });
});

describe('handleFormErrors', () => {
  let messageDiv, errorsDiv;

  beforeEach(() => {
    messageDiv = document.createElement('div');
    errorsDiv = document.createElement('div');
  });

  test('renders error list correctly', () => {
    const errors = {
      title: 'Missing title',
      author: 'Author name too short'
    };

    handleFormErrors(errorsDiv, errors);

    expect(errorsDiv.innerHTML).toBe(
      '<ul><li><strong>title</strong>: Missing title</li><li><strong>author</strong>: Author name too short</li></ul>'
    );
  });
});
