function ready(fn) {
  if (document.readyState != 'loading'){
    fn();
  } else {
    document.addEventListener('DOMContentLoaded', fn);
  }
}

function request(method, url, params) {
  let data = params.data;

  if(!data) {
    data = {};
  }

  var xhr = new XMLHttpRequest();

  if(method === 'GET' && data) {
    let urlSuffix = '?' + Object.keys(data).map(
      key => key + '=' + encodeURIComponent(data[key])
    ).join('&');
    xhr.open(method, url + urlSuffix, true);
  } else {
    xhr.open(method, url, true);
  }

  xhr.responseType = 'json';

  xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');

  if(params.headers) {
    for (const [key, value] of Object.entries(params.headers)) {
        xhr.setRequestHeader(key, value);
    }
  }

  xhr.onload = () => {
    if (xhr.status >= 200 && xhr.status < 400) {
      var data = xhr.response;

      if(params.onSuccess) {
        params.onSuccess(data);
      }
    } else {
      console.log('We reached our target server, but it returned an error');
      console.log(xhr);
    }
  };

  xhr.onerror = () => {
    console.log('There was a connection error of some sort');
  };

  if(method === 'GET') {
    xhr.send();
  } else {
    xhr.send(JSON.stringify(data));
  }
}

function get(url, params) {
  return request('GET', url, params);
}

function post(url, params) {
  return request('POST', url, params);
}

function put(url, params) {
  return request('PUT', url, params);
}

function delete_(url, params) {
  return request('DELETE', url, params);
}
