import http from 'k6/http';
import { check, group, sleep } from 'k6';

// Repo-local smoke test. It targets the service under test, never a sibling
// repository path (the old `../viavitae-qa/load/assessment.js` reference only
// resolved inside the monorepo and silently no-oped elsewhere). nightly-e2e.yml
// runs this against the compose stack; locally, point BASE_URL at your dev server.
//
//   k6 run deployments/k6/smoke.js
//   BASE_URL=https://api.staging.viavitae.eu k6 run deployments/k6/smoke.js
const BASE_URL = (__ENV.BASE_URL || 'http://localhost:8000').replace(/\/$/, '');

export const options = {
  vus: 5,
  duration: '20s',
  // Scaffolded mutations answer 501/422 by design, so a global http_req_failed
  // gate would be meaningless. Thresholds are on latency and on the explicit
  // contract checks below, which is what actually matters for a smoke test.
  thresholds: {
    http_req_duration: ['p(95)<800'],
    checks: ['rate>0.99'],
  },
};

const JSON_HEADERS = { headers: { 'Content-Type': 'application/json' } };

// errCode returns the unified envelope's error.code, or null if the body is not
// the expected shape. It never throws, so a check reports false rather than
// crashing the VU.
function errCode(body) {
  try {
    const parsed = JSON.parse(body);
    return parsed && parsed.error && typeof parsed.error.code === 'string'
      ? parsed.error.code
      : null;
  } catch (_e) {
    return null;
  }
}

function hasRequestId(body) {
  try {
    const parsed = JSON.parse(body);
    return !!(parsed && parsed.error && 'request_id' in parsed.error);
  } catch (_e) {
    return false;
  }
}

export default function () {
  group('health and version', function () {
    const live = http.get(`${BASE_URL}/health/live`);
    check(live, { 'liveness probe is 200': (r) => r.status === 200 });

    const health = http.get(`${BASE_URL}/v1/health`);
    check(health, { 'v1 health is 200': (r) => r.status === 200 });

    const version = http.get(`${BASE_URL}/v1/version`);
    check(version, {
      'v1 version is 200': (r) => r.status === 200,
      'v1 version names the service': (r) => r.json('service') === 'viavitae-api',
    });

    // Readiness depends on the database; 200 (up) and 503 (degraded) are both
    // valid smoke outcomes, a 5xx crash or a timeout is not.
    const ready = http.get(`${BASE_URL}/v1/ready`);
    check(ready, { 'v1 ready is 200 or 503': (r) => r.status === 200 || r.status === 503 });
  });

  group('assessment contract', function () {
    // A well-formed submission reaches the handler. The handler is scaffolded, so
    // it must answer 501 not_implemented -- never a 500 stack trace.
    const valid = http.post(
      `${BASE_URL}/v1/assessment/`,
      JSON.stringify({ parish: 'Smoke Parish', congregation_size: 120, locale: 'lt' }),
      JSON_HEADERS
    );
    check(valid, {
      'valid assessment is 501 (scaffolded)': (r) => r.status === 501,
      'valid assessment uses the error envelope': (r) => hasRequestId(r.body),
      'valid assessment code is not_implemented': (r) => errCode(r.body) === 'not_implemented',
    });

    // An empty body fails validation before any side effect: 422, not 500.
    const invalid = http.post(`${BASE_URL}/v1/assessment/`, JSON.stringify({}), JSON_HEADERS);
    check(invalid, {
      'empty assessment is 422': (r) => r.status === 422,
      'empty assessment code is validation_error': (r) => errCode(r.body) === 'validation_error',
    });
  });

  sleep(0.2);
}
